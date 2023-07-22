
#include <pybind11/pybind11.h>
#include <string>
#include <fstream>
#include <vector>
#include <iostream>
#include <math.h>
#include <stdio.h>
#include <thread>
#include <mutex>

namespace py = pybind11;
using namespace std;
using namespace py;

void update_db(string country){
    mutex mtx;
    lock_guard<mutex> lg(mtx);
    ifstream infile(countriesPath,ifstream::binary);
    int i = 1;
    int country_name_len = country.length();
    int* jumping_indexes = new int[country_name_len];
    jumping_indexes[0] = 0;
    int len = 0;
    while(i<country_name_len){
        if(country[i] == country[len]){
            len++;
            jumping_indexes[i]=len;
            i++;
        }
        else{
            if( len != 0){
                len = jumping_indexes[len-1];
            }
            else{
                jumping_indexes[i] = 0;
                i++;
            }
        }
    }
    infile.seekg(0,infile.end);
    long size = infile.tellg();
    infile.seekg(0);
    char* buffer = new char[size];
    infile.read(buffer,size);
    char* current_letter = &buffer[0];
    i = 0;
    int j = 0;
    while(country_name_len-j <= size-i){
        if(country[j]==*(buffer+i)){
            i++;
            j++;
        }
        if(j == country_name_len){
            i++;
            int tmp_i = i;
            string number = "";
            while(*(buffer + tmp_i) != '\n'){
                number += *(buffer + tmp_i);
                tmp_i++;
            }
            int number_length = number.length();
            int step = 1;
            int entry_count = 0;
            string::iterator current_digit = number.begin();
            while(current_digit != number.end()){
                entry_count += *current_digit - '0' * pow(10,number_length-step);
                current_digit++;
                step++;
            }
            entry_count++;
            //cout << entry_count << endl;
            step = 0;
            number = "";
            int past_number = 0;
            while(float(entry_count)/pow(10,step)>= 1.0){
                int modula = pow(10,step+1);
                int div = (entry_count % modula)/pow(10,step);
                string ascii = "";
                ascii += char(div+'0');
                number.insert(0,ascii);
                //cout<<div<<endl;
                past_number = entry_count % modula;
                step++;
            }
            //cout<<number<<endl;
            if(number.length()==number_length){
                int tmp_len = 0;
                while(i!=tmp_i){
                    buffer[i]=number[tmp_len];
                    tmp_len++;
                    i++;
                }
                remove(countriesPath);
                ofstream outfile(countriesPath,ofstream::binary);
                outfile.write(buffer,size);
                outfile.close();
                number.clear();
                break;
            }
            char* new_buffer = new char[size+1];
            int index = 0;
            while(index!=i){
                new_buffer[index] = buffer[index];
                index++;
            }
            int tmp_index = 0;
            while(tmp_index != number_length+1){
                new_buffer[index+tmp_index] = number[tmp_index];
                tmp_index++;
            }
            index+= tmp_index;
            while(tmp_i != size){
                new_buffer[index] = buffer[tmp_i];
                index++;
                tmp_i++;
            }
            remove(countriesPath);
            ofstream outfile(countriesPath,ofstream::binary);
            outfile.write(new_buffer,size);
            outfile.close();
            number.clear();
            delete[] new_buffer;
            break;
        }
        else if(i<size && country[j] != *(buffer + i)){

            if(j != 0){
                j = jumping_indexes[j-1];
            }
            else{
                i += 1;
            }
        }
    }

    delete[] buffer;
    delete[] jumping_indexes;
    infile.close();
}
/*
int main(){
    update_db("TURKEY");
    return 0;
}
*/

PYBIND11_MODULE(update_db,m){
    m.doc() = "This module have been created by https://github.com/Musa-Sina-Ertugrul \nThis module has only one function that update countries.txt \naccording to individual entries to PROT-ON website";
    m.def("update_db",&update_db,"function takes name of country as uppercase then icrement its number by 1. Then do necessery changes in file");
}