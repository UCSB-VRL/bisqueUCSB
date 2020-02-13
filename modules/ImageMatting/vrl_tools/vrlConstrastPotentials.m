function weights = vrlConstrastPotentials(I, edges, nlSigma)

I = double(I);
% I = imfilter( I, fspecial('gauss', [11 11], 1.8 ), 'same', 'conv' );
I = kovesi_anisodiff(I, 40, 20, .25, 1);
[Ix Iy] = gradient(I);
gradMag = sqrt(Ix.^2 + Iy.^2);

% weights = exp( - ( I(edges(:,1)) - I(edges(:,2)) ).^2 / (2*nlSigma^2) );
weights = exp( -gradMag(edges(:,1)) ./  (2*nlSigma^2) );
tempImg1 = zeros(size(I,1), size(I,2));
tempImg2 = zeros(size(I,1), size(I,2));
tempImg1( edges(:,1) ) = weights; tempImg2( edges(:,2) ) = weights;
figure(1); imagesc( (tempImg1 + tempImg2 ) / 2); title([num2str(nlSigma) ] );

return;

