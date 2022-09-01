function vrlContour( maskImg , inpColor)

hold on;
cc = contour(maskImg, [0.5, 0.5]);
cc2 = get_contours(cc);
for i = 1:length(cc2)
    plot(cc2{i}(1, :), cc2{i}(2, :), 'Color', inpColor, 'Linewidth', 3);
end
hold off;