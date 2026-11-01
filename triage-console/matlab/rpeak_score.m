function s = rpeak_score(det, ref, fs)
% RPEAK_SCORE  Compare detected R-peaks with reference annotations.
%   A detection counts as correct if it is within +-75 ms of an unused reference beat.
t = round(0.075 * fs); used = false(size(ref)); tp = 0;
for d = det(:)'
    [dist, k] = min(abs(ref(:) - d) + used(:) * 1e9);
    if dist <= t, used(k) = true; tp = tp + 1; end
end
s.tp = tp; s.fp = numel(det) - tp; s.fn = numel(ref) - tp;
s.sensitivity = tp / (tp + s.fn);
s.ppv = tp / (tp + s.fp);
end
