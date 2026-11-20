clear; clc;
cfg = config();
policy_names = {'wait_all','fixed20','adaptive'};
duties = [0.1 0.3 0.6];
num_busy_list = [1 2 3];
seeds = 1:10;

results = struct('num_busy',{},'duty',{},'seed',{},'policy',{}, ...
    'goodput',{},'wait_mean',{},'wait_p95',{},'fail_rate',{});

for nb = num_busy_list
    for d = duties
        for s = seeds
            cfg.num_busy = nb;
            cfg.duty = d;
            cfg.seed = s;
            state = gen_trace(cfg);
            for p = 1:length(policy_names)
                res = simulate(cfg, state, policy_names{p});
                results(end+1) = struct( ...
                    'num_busy', nb, 'duty', d, 'seed', s, ...
                    'policy', policy_names{p}, ...
                    'goodput', res.goodput_Mbps, ...
                    'wait_mean', res.wait_mean, ...
                    'wait_p95', res.wait_p95, ...
                    'fail_rate', res.fail_rate); %#ok<SAGROW>
            end
        end
    end
end

% Summarise the mean and 95% confidence interval by num_busy, duty and policy.
fprintf('\nSummary (mean ± 95%% CI over %d seeds):\n', length(seeds));
for nb = num_busy_list
    for d = duties
        fprintf('\n-- num_busy=%d, duty=%.1f --\n', nb, d);
        for p = 1:length(policy_names)
            vals = [];
            for r = 1:length(results)
                if results(r).num_busy==nb && results(r).duty==d && ...
                        strcmp(results(r).policy, policy_names{p})
                    vals(end+1) = results(r).goodput; %#ok<AGROW>
                end
            end
            m = mean(vals);
            ci = 1.96 * std(vals) / sqrt(length(vals));
            fprintf('  %-9s: %6.1f ± %4.1f Mbps\n', policy_names{p}, m, ci);
        end
    end
end

% Plot goodput against duty cycle for each value of num_busy.
for nb = num_busy_list
    figure; hold on; grid on;
    for p = 1:length(policy_names)
        m = zeros(1,length(duties));
        ci = zeros(1,length(duties));
        for j = 1:length(duties)
            vals = [];
            for r = 1:length(results)
                if results(r).num_busy==nb && results(r).duty==duties(j) && ...
                        strcmp(results(r).policy, policy_names{p})
                    vals(end+1) = results(r).goodput; %#ok<AGROW>
                end
            end
            m(j) = mean(vals);
            ci(j) = 1.96*std(vals)/sqrt(length(vals));
        end
        errorbar(duties, m, ci, '-o', 'LineWidth', 1.5);
    end
    xlabel('Interference duty cycle');
    ylabel('Goodput (Mbps)');
    title(sprintf('Goodput vs duty, num\\_busy=%d', nb));
    legend(policy_names, 'Location','best');
end
