if __name__ == '__main__':
    file = open('Triple-count.tsv', 'rU')
    triple_count = file.read()
    file.close()
    
    overall_1 = 0
    for count in triple_count.split():
        overall_1 = overall_1 + int(count)
        
    #print overall
    
    file = open('black_list_triple_count', 'rU')
    black_list = file.read()
    file.close()
    
    file = open('csv_file_lines','rU')
    csv_file_lines = file.read()
    file.close()
    
    overall_2 = 0
    file_lines = {}
    for file_line in csv_file_lines.split('\n'):
        id = file_line.split()[1]
        id = id[6:]
        lines = int(file_line.split()[0])
        file_lines[id] = lines
    
    summary_lines = 0
    for id in file_lines:
        summary_lines = summary_lines + file_lines[id]
    
    print summary_lines
    
    for item in black_list.split('\n'):
        id = item.split()[0]
        column_count = int(item.split()[1])
        triples = column_count * file_lines[id]
        overall_2 = overall_2 + triples
    
    print overall_2
    print overall_1
    print overall_1 + overall_2
    #112346924