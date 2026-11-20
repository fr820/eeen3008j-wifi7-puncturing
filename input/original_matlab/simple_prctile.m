function v = simple_prctile(x, p)
% Compute a simple percentile without the Statistics Toolbox.
if isempty(x)
    v = NaN;
    return;
end
x = sort(x);
n = length(x);
idx = max(1, min(n, round(p/100*n + 0.5)));
v = x(idx);
end
