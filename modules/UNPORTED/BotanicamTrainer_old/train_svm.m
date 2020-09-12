function train_svm(kernel,ClassifierMethod,foldername)

%runs the libsvm training on the specified kernel

%kernels:
%0 = linear
%1 = polynomial
%2 = rbf
%3 = sigmoid

%2 reccomended by Lin&Lin, though 0 may be faster

if strcmp(ClassifierMethod,'Bush Descriptor')
    type = 'bush';
elseif strcmp(ClassifierMethod, 'Leaf Descriptor')
    type = 'leaf';
end

disp('scaling data...');

    if ~ispc
        system(sprintf('svm-scale -s %s/%sscaledata training_features > training_features_scaled',foldername,type));
    else
        system(sprintf('svm-scale -s %s/%sscaledata training_features > training_features_scaled',foldername,type));
    end

    disp('creating model...');

    if ~ispc
        system(sprintf('svm-train -q -b 1 -t %d training_features_scaled %s/%smodel', kernel,foldername,type));
    else
        system(sprintf('svm-train -q -b 1 -t %d training_features_scaled %s/%smodel', kernel,foldername,type));
    end

end