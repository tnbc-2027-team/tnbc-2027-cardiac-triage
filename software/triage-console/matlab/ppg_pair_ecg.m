function [pat, d0] = ppg_pair_ecg(rpeaks, feet, fs)
% PPG_PAIR_ECG  Pulse arrival time (R-peak to PPG foot) for each ECG beat, in seconds.
%   [pat, d0] = ppg_pair_ecg(rpeaks, feet, fs)
%   1. Typical delay d0 = most common R-to-foot delay between 80 and 800 ms (10 ms bins)
%   2. Each R-peak takes the foot closest to R + d0, within +-min(120 ms, 30% of RR)
%   Beats with no matching pulse get NaN. Works when the delay is longer than
%   one heartbeat (fast heart rates).
lo = 0.08; hi = 0.8;
f = sort(feet(~isnan(feet))); f = f(:)';
rpeaks = rpeaks(:)';
pat = nan(size(rpeaks)); d0 = NaN;
if numel(f) < 3 || numel(rpeaks) < 3, return; end
delays = [];
for r = rpeaks
    dd = (f - r) / fs;
    delays = [delays, dd(dd >= lo & dd < hi)]; %#ok<AGROW>
end
if isempty(delays), return; end
edges = lo:0.01:hi;
counts = zeros(1, numel(edges) - 1);
for k = 1:numel(counts), counts(k) = sum(delays >= edges(k) & delays < edges(k + 1)); end
[~, m] = max(counts);
d0 = edges(m) + 0.005;
tol = min(0.12, 0.3 * median(diff(rpeaks)) / fs);
for k = 1:numel(rpeaks)
    err = abs((f - rpeaks(k)) / fs - d0);
    [e, j] = min(err);
    if e <= tol, pat(k) = (f(j) - rpeaks(k)) / fs; end
end
end
