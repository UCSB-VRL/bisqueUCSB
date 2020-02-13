function [nuclei] = classify( nuclei, min_bound )
  
    num_nuclei = length(nuclei);
    for n=1:num_nuclei,
       nuclei{n}.class = 1;
    end       

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
    % compute decriptors
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
    for n=1:num_nuclei,
       PHFmean(n) = mean(nuclei{n}.ROIphf(:));
       PHFstd(n)  = std(double(nuclei{n}.ROIphf(:)));
    end        
    phf_m = PHFstd.*PHFmean;
    %phf_m = PHFmean;
    
    %fprintf('nuclei PHF mean: %f std: %f\n', mean(PHFmean(:)), std(PHFmean(:)) );
    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
    % K-means iterations
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%     
    l = min(phf_m);
    u = max(phf_m);
    low_bound = u;   
    
    total_itearations = 0;
    updated = true;
    while (updated~=false) || (total_itearations<1000),
        updated = false;        
        for i=1:num_nuclei,
          %if (u-phf_m(i) > phf_m(i)-l) || (phf_m(i) < min_bound*PHFstd(i) ),
          if (u-phf_m(i) > phf_m(i)-l) || (phf_m(i) < min_bound ),
            if nuclei{i}.class ~= 1, 
                nuclei{i}.class = 1; updated = true;
            end
          else    
            if nuclei{i}.class ~= 2, 
                nuclei{i}.class = 2; updated = true;
            end
          end
        end
        
        total_itearations = total_itearations + 1;
        
        % update centroids
        c1 = []; c2 = [];
        for i=1:num_nuclei,
          if nuclei{i}.class > 1,  
              c1 = [c1, phf_m(i)];
          else
              c2 = [c2, phf_m(i)];
          end; 
        end;
        u = mean(c1);
        l = mean(c2);     
    end
   
end