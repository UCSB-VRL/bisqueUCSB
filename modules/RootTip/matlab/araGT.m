function [] = araGT(path)    
    [A MID TTT] = getMidlines({path},1,0);        
    % get the growth rate    
    for j = 1:size(MID{1},2)        
        L(j) = size(MID{1}{j},1);
    end
    csvwrite(['./gr.csv'],gradient(L'))
    csvwrite(['./angle.csv'],-A{1}'*180/pi)
    csvwrite(['./tips.csv'],TTT)
end
%{
    araGT('Y:\for logans visit\data\arabidopsis root gravitropism\031810_c1n0_10 mM Scu_pgm-1_5d old\031810_c1n0_10 mM Scu_pgm-1_5d old\');
%}
