function[contours]=bounda(phi);

d=size(phi,3);
count=1;
   
  for j=1:d
        contours_old = bwboundaries(phi(:,:,j));
        for jj=1:size(contours_old,1)
            
            contours_new{jj}(:,1:2)=contours_old{jj}(:,1:2);
            contours_new{jj}(:,3)=j;
            
            contours{j}=contours_new';
           
        end
         clear contours_new;
    end
    