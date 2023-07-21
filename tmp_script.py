#to make 0 every data
with open("countries.txt","r+") as file:
    lines = file.readlines()
    new_lines = []
    for line in lines:
        tmp_str = ""
        for i in range(len(line)-1,-1,-1):
            if line[i] == '\t':
                if not len(line[:i])==1:
                    tmp_str = line[:i]+"\t0\n"
                break
        new_lines.append(tmp_str)
    file.writelines(new_lines)
