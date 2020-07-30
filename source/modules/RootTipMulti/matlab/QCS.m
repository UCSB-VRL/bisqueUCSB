function [D U BV] = spec_QCS(D,SW,NDIM,U,BV)
switch SW
    case 1
        % query
        temp = D(:,11:end);
        % compress
        if size(BV,1) ~=0
            [SIM C ERR] = PCA_REPROJ(temp,BV,U);
        else
            [SIM U BV L C ERR] = PCA_FIT(temp,NDIM);
        end
        % stack
        D = [C ERR];
    case 2
        % put other stuff here
end


    
