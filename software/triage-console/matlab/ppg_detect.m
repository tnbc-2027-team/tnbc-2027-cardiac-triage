function [peaks, feet, info] = ppg_detect(x, fs, invert)
% PPG_DETECT  Systolic peaks and pulse feet (onsets) in a PPG signal.
%   [peaks, feet, info] = ppg_detect(x, fs) returns systolic peak sample indices
%   (1-based) and pulse foot times in fractional samples for PPG vector x
%   sampled at fs Hz. Same steps as the console's PPG tab and python/ppg.py:
%     1. Bandpass 0.5-8 Hz (biquad high-pass + low-pass, forward and backward)
%     2. Orientation: an upright PPG rises faster than it falls. Raw sensor IR
%        (e.g. MAX30102) is upside down and is flipped automatically.
%        Pass invert = true/false to force it.
%     3. Systolic peaks (Elgendi et al. 2013): clip negatives, square, moving
%        averages over 111 ms and 667 ms; each block where the short average is
%        above the long average + 0.02*mean and at least 111 ms wide holds one
%        peak (its highest point); 300 ms refractory
%     4. Pulse foot by tangent intersection: the tangent at the steepest upslope
%        meets the horizontal line through the preceding minimum
%     5. Pulse quality: correlation with the median pulse >= 0.8 and amplitude
%        between 0.3x and 3x the typical amplitude
%   Uses base MATLAB only (no Signal Processing Toolbox).
%
%   info fields: filtered, inverted, template, corr, clean (logical per pulse),
%                pulse_rate_bpm, pp_variation, clean_pct
%
%   Example (run from the repo root):
%     d = readmatrix('data/ppg_resting_100hz.csv');   % time_s, ppg, ecg_mV
%     fs = 100; [pk, ft, info] = ppg_detect(d(:,2), fs);
%     t = d(:,1); plot(t, info.filtered); hold on
%     plot(t(pk), info.filtered(pk), 'ro');
%     plot((ft - 1) / fs, interp1(1:numel(t), info.filtered, ft), 'k^'); xlim([0 10])

x = x(:) - median(x);
s = fwdbwd(biquad('hp', 0.5, fs), x);
s = fwdbwd(biquad('lp', 8, fs), s);

if nargin < 3 || isempty(invert)
    d = diff(s);
    invert = prctile_lin(d, 99.5) < -prctile_lin(d, 0.5);
end
if invert, s = -s; end

peaks = systolic_peaks(s, fs);
feet = pulse_feet(s, peaks, fs);
[corr, clean, tpl] = beat_quality(s, peaks);

pp = diff(peaks(:)) / fs;
okpp = clean(2:end) & clean(1:end-1);
use = pp(okpp);
if numel(use) < 3, use = pp; end

info.filtered = s;
info.inverted = logical(invert);
info.template = tpl;
info.corr = corr;
info.clean = clean;
info.pulse_rate_bpm = 60 / median(use);
info.pp_variation = std(use, 1) / mean(use);
info.clean_pct = 100 * mean(clean);
end

% ---------------------------------------------------------------------------
function pk = systolic_peaks(s, fs)
y = s; y(y < 0) = 0; y = y .^ 2;
maPeak = movavg(y, round(0.111 * fs));
maBeat = movavg(y, round(0.667 * fs));
on = maPeak > maBeat + 0.02 * mean(y);
minW = round(0.111 * fs);
edges = diff([0; on; 0]);
starts = find(edges == 1); stops = find(edges == -1) - 1;
pk = [];
for k = 1:numel(starts)
    if stops(k) - starts(k) + 1 >= minW
        [~, j] = max(s(starts(k):stops(k)));
        pk(end + 1) = starts(k) + j - 1; %#ok<AGROW>
    end
end
refr = round(0.3 * fs); out = [];
for p = pk
    if ~isempty(out) && p - out(end) < refr
        if s(p) > s(out(end)), out(end) = p; end
    else
        out(end + 1) = p; %#ok<AGROW>
    end
end
pk = out;
end

function feet = pulse_feet(s, pk, fs)
d = gradient(s);
feet = nan(size(pk));
for k = 1:numel(pk)
    p = pk(k);
    lo = max(1, p - round(0.6 * fs));
    if k > 1, lo = max(lo, pk(k - 1)); end
    if p - lo < 3, continue; end
    [~, j] = min(s(lo:p)); m = lo + j - 1;
    if p - m < 2, continue; end
    [~, j] = max(d(m:p)); sl = m + j - 1;
    if d(sl) <= 0, continue; end
    f = sl - (s(sl) - s(m)) / d(sl);
    feet(k) = min(max(f, m), sl);
end
end

function [corr, clean, tpl] = beat_quality(s, pk)
n = numel(pk); corr = zeros(1, n); clean = false(1, n); tpl = [];
if n < 3, return; end
T = median(diff(pk));
a = round(0.35 * T); b = round(0.65 * T);
ok = find(pk - a >= 1 & pk + b - 1 <= numel(s));
beats = zeros(numel(ok), a + b);
for j = 1:numel(ok), beats(j, :) = s(pk(ok(j)) - a:pk(ok(j)) + b - 1); end
tpl = median(beats, 1);
for j = 1:numel(ok)
    c = corrcoef(beats(j, :), tpl); corr(ok(j)) = c(1, 2);
end
amp = zeros(1, n);
for k = 1:n, amp(k) = s(pk(k)) - min(s(max(1, pk(k) - a):pk(k))); end
medAmp = median(amp);
clean = corr >= 0.8 & amp >= 0.3 * medAmp & amp <= 3 * medAmp;
end

function y = movavg(x, w)
w = max(1, w); n = numel(x); half = floor(w / 2);
c = [0; cumsum(x(:))];
i = (1:n)';
lo = min(n, max(0, i - 1 - half)); hi = min(n, max(0, i - 1 - half + w));
y = (c(hi + 1) - c(lo + 1)) / w;
end

function v = prctile_lin(x, p)
x = sort(x(:)); pos = (numel(x) - 1) * p / 100 + 1;
lo = floor(pos); hi = ceil(pos);
v = x(lo) + (x(hi) - x(lo)) * (pos - lo);
end

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
