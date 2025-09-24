#include <iostream>
using namespace std;

// Copy to pi:
// scp -r "C:\Users\matt\Documents\GitHub\Chess-Robot\Raspberry-Pi-Embedded-C++\*.cpp" matt@10.0.0.188:/home/matt/Chess-Robot/Cpp
// I copy files to the pi instead of SSHing in with VSCode because the pi makes annoying sounds
// when I do that :)
// Compile on Pi:
// g++ *.cpp -o program


int main() {
    cout << "Hello, Raspberry Pi!" << endl;
    return 0;
}
