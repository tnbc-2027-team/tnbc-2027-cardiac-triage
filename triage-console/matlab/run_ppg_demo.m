% RUN_PPG_DEMO  PPG pulse detection + check against the simultaneous ECG.
% Run from the repo root (the folder that holds data/ and matlab/):
%   addpath matlab; run_ppg_demo
% Uses base MATLAB only.

files = {'data/ppg_resting_100hz.csv', 100; 'data/ppg_icu_a103l_250hz.csv', 250};

for i = 1:size(files, 1)
    d = readmatrix(files{i, 1});          % columns: time_s, ppg, ecg
    fs = files{i, 2};
    t = d(:, 1); ppg = d(:, 2); ecg = d(:, 3);

    [pk, ft, info] = ppg_detect(ppg, fs);
    rp = rpeak_detect(ecg, fs);
    [pat, d0] = ppg_pair_ecg(rp, ft, fs);
    pv = sort(pat(~isnan(pat)));
    q = @(p) interp1(0:numel(pv) - 1, pv, (numel(pv) - 1) * p / 100);   % percentile

    fprintf('\n%s\n', files{i, 1});
    fprintf('  pulses detected      %d (%.1f%% clean)\n', numel(pk), info.clean_pct);
    fprintf('  pulse rate           %.1f bpm\n', info.pulse_rate_bpm);
    fprintf('  ECG heart rate       %.1f bpm (%d R-peaks)\n', 60 / median(diff(rp) / fs), numel(rp));
    fprintf('  ECG beats w/ pulse   %.1f%%\n', 100 * mean(~isnan(pat)));
    fprintf('  pulse arrival time   %.0f ms median (IQR %.0f-%.0f ms)\n', ...
        1000 * median(pv), 1000 * q(25), 1000 * q(75));

    figure('Name', files{i, 1});
    win = t <= 10;
    subplot(2, 1, 1);
    plot(t(win), ecg(win)); hold on
    rw = rp(rp <= find(win, 1, 'last'));
    plot(t(rw), ecg(rw), 'ro'); title('ECG with R-peaks'); ylabel('mV')
    subplot(2, 1, 2);
    s = info.filtered;
    plot(t(win), s(win)); hold on
    pw = pk(pk <= find(win, 1, 'last'));
    plot(t(pw), s(pw), 'ro');
    fw = ft(~isnan(ft) & ft <= find(win, 1, 'last'));
    plot((fw - 1) / fs, interp1(1:numel(s), s, fw), 'k^');
    title('PPG: systolic peaks (o) and pulse feet (^)'); xlabel('time (s)')
end

