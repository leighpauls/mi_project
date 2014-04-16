for i = 1:size(all_data, 1)
    if rand() < 0.7
        test_data = cat(1, test_data, all_data(i,:));
    else
        training_data = cat(1, training_data, all_data(i,:));
    end
end
    