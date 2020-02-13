function tr = generate_tr(S, var1, var2)

mid = (S+1)/2;
al = 1 : S;
tr = zeros(S);
no = exp(-(al-mid).^2/(2*var2));
no = no / sum(no);
    
for i = 1 : S
    tr(i,:) = exp(-(al-i).^2/(2*var1));
    tr(i,:) = tr(i,:) .* no;
    tr(i,:) = tr(i,:) / sum(tr(i,:));
end


end