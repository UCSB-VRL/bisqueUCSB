function obs = calculate_obss(gradients,my_path);
N=size(my_path,1);
for i=2:N
    obs(i)=calculate_obs(gradients,my_path(i-1,2),my_path(i,2),my_path(i-1,1),my_path(i,1));
end
