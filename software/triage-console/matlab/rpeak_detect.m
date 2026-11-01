function [peaks, info] = rpeak_detect(x, fs)
% RPEAK_DETECT  R-peak detection by QRS template matching.
%   [peaks, info] = rpeak_detect(x, fs) returns R-peak sample indices (1-based)
%   for ECG vector x sampled at fs Hz. Same steps as js/ecg.js and python/rpeak.py:
%     1. Bandpass 5-15 Hz (biquad high-pass + low-pass, forward and backward)
%     2. First pass: derivative -> square -> 150 ms moving average -> adaptive threshold
%     3. Template = median beat around the first-pass R-peaks
%     4. Normalized cross-correlation with the template (> 0.5, amplitude gate 40%,
%        200 ms refractory)
%     5. Move each beat to the largest |bandpassed| sample within +-50 ms
%   Uses base MATLAB only (no Signal Processing Toolbox).
%
%   Example (run from the repo root):
%     d = readmatrix('data/mitdb100_5min.csv');           % time_s, ecg_mV
%     fs = 360; [pk, info] = rpeak_detect(d(:,2), fs);
%     ref = round(readmatrix('data/mitdb100_5min_rpeaks.csv') * fs) + 1;
%     s = rpeak_score(pk, ref, fs)                        % sensitivity / PPV
%     t = d(:,1); plot(t, d(:,2)); hold on; plot(t(pk), d(pk,2), 'ro'); xlim([0 10])

x = x(:) - median(x);
bp = fwdbwd(biquad('hp', 5, fs), x);
bp = fwdbwd(biquad('lp', 15, fs), bp);

fp = first_pass(bp, fs);
[tpl, offset] = build_template(bp, fp, fs);
r = ncc(bp, tpl);

amp = median(abs(bp(fp)));
refr = floor(0.2 * fs); h = floor(0.05 * fs);
isPk = [false; r(2:end-1) > 0.5 & r(2:end-1) >= r(1:end-2) & r(2:end-1) >= r(3:end); false];
cand = find(isPk);
[~, order] = sort(r(cand), 'descend');
cand = cand(order);
picked = [];
for i = cand'
    p = i + offset;
    seg = bp(max(1, p - h):min(numel(bp), p + h));
    if max(abs(seg)) < 0.4 * amp, continue; end
    if any(abs(picked - i) <= refr), continue; end
    picked(end + 1) = i; %#ok<AGROW>
end
peaks = refine(bp, sort(picked) + offset, fs);

rr = diff(peaks) / fs;
info.bandpassed = bp;
info.template = tpl;
info.first_pass = fp;
info.hr_bpm = 60 / median(rr);
info.rr_variation = std(rr, 1) / mean(rr);
end

% ---------------------------------------------------------------------------
function c = biquad(kind, f0, fs)
w = 2 * pi * f0 / fs; q = 1 / sqrt(2);
alpha = sin(w) / (2 * q); cw = cos(w);
if strcmp(kind, 'hp'), b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2];
else, b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; end
a = [1 + alpha, -2 * cw, 1 - alpha];
c.b = b / a(1); c.a = a / a(1);
end

function y = fwdbwd(c, x)
y = filter(c.b, c.a, x);
y = flipud(filter(c.b, c.a, flipud(y)));
end

function pk = first_pass(bp, fs)
d = [0; diff(bp)]; sq = d .^ 2;
w = floor(0.15 * fs);
mwi = conv(sq, ones(w, 1) / w, 'same');
refr = floor(0.2 * fs);
init = mwi(1:min(end, 2 * floor(fs)));
spk = 0.5 * max(init); npk = 0.5 * mean(init);
pk = []; last = -refr;
for i = 2:numel(mwi) - 1
    if mwi(i) > mwi(i - 1) && mwi(i) >= mwi(i + 1)
        thr = npk + 0.25 * (spk - npk);
        if mwi(i) > thr && i - last > refr
            pk(end + 1) = i; last = i; %#ok<AGROW>
            spk = 0.125 * mwi(i) + 0.875 * spk;
        else
            npk = 0.125 * mwi(i) + 0.875 * npk;
        end
    end
end
pk = refine(bp, pk, fs);
end

function out = refine(bp, idx, fs)
h = floor(0.05 * fs); out = zeros(size(idx));
for k = 1:numel(idx)
    lo = max(1, idx(k) - h); hi = min(numel(bp), idx(k) + h);
    [~, j] = max(abs(bp(lo:hi)));
    out(k) = lo + j - 1;
end
out = unique(out);
end

function [tpl, a] = build_template(bp, pk, fs)
a = floor(0.10 * fs); b = floor(0.15 * fs);
pk = pk(pk - a >= 1 & pk + b - 1 <= numel(bp));
beats = zeros(numel(pk), a + b);
for k = 1:numel(pk), beats(k, :) = bp(pk(k) - a:pk(k) + b - 1); end
tpl = median(beats, 1)';
end

function r = ncc(bp, tpl)
n = numel(tpl);
t = tpl - mean(tpl); t = t / (norm(t) + 1e-12);
num = conv(bp, flipud(t), 'valid');
c1 = [0; cumsum(bp)]; c2 = [0; cumsum(bp .^ 2)];
s1 = c1(n + 1:end) - c1(1:end - n);
s2 = c2(n + 1:end) - c2(1:end - n);
r = num ./ sqrt(max(s2 - s1 .^ 2 / n, 1e-12));
end
