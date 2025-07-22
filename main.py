# -*-coding:utf-8 -*-
import sys
import time

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.key_binding import KeyBindings
from init import Init
bindings = KeyBindings()
@bindings.add('c-c')
def _(event):
    " Exit when `ctrl-c` is pressed. "
    event.app.exit()


def main():
    # 主函数
    # input_memory_history = InMemoryHistory()
    print('''                                                                                                                                                                                                                                
               AAA                  CCCCCCCCCCCCCFFFFFFFFFFFFFFFFFFFFFF                                                    
              A:::A              CCC::::::::::::CF::::::::::::::::::::F                                                    
             A:::::A           CC:::::::::::::::CF::::::::::::::::::::F                                                    
            A:::::::A         C:::::CCCCCCCC::::CFF::::::FFFFFFFFF::::F                                                    
           A:::::::::A       C:::::C       CCCCCC  F:::::F       FFFFFFuuuuuu    uuuuuu  zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
          A:::::A:::::A     C:::::C                F:::::F             u::::u    u::::u  z:::::::::::::::zz:::::::::::::::z
         A:::::A A:::::A    C:::::C                F::::::FFFFFFFFFF   u::::u    u::::u  z::::::::::::::z z::::::::::::::z 
        A:::::A   A:::::A   C:::::C                F:::::::::::::::F   u::::u    u::::u  zzzzzzzz::::::z  zzzzzzzz::::::z  
       A:::::A     A:::::A  C:::::C                F:::::::::::::::F   u::::u    u::::u        z::::::z         z::::::z   
      A:::::AAAAAAAAA:::::A C:::::C                F::::::FFFFFFFFFF   u::::u    u::::u       z::::::z         z::::::z    
     A:::::::::::::::::::::AC:::::C                F:::::F             u::::u    u::::u      z::::::z         z::::::z     
    A:::::AAAAAAAAAAAAA:::::AC:::::C       CCCCCC  F:::::F             u:::::uuuu:::::u     z::::::z         z::::::z      
   A:::::A             A:::::AC:::::CCCCCCCC::::CFF:::::::FF           u:::::::::::::::uu  z::::::zzzzzzzz  z::::::zzzzzzzz
  A:::::A               A:::::ACC:::::::::::::::CF::::::::FF            u:::::::::::::::u z::::::::::::::z z::::::::::::::z
 A:::::A                 A:::::A CCC::::::::::::CF::::::::FF             uu::::::::uu:::uz:::::::::::::::zz:::::::::::::::z
AAAAAAA                   AAAAAAA   CCCCCCCCCCCCCFFFFFFFFFFF               uuuuuuuu  uuuuzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz                                                                                                                                                                                                                                                                                                                           
''')
    input_word_completer = WordCompleter(
        ['help',
         'start',
         'exit']
    )
    prompt_session = PromptSession('[>>] ', completer=input_word_completer, cursor=CursorShape.BLINKING_BEAM,
                                   key_bindings=bindings)
    init = Init()
    while True:
        prompt_input = prompt_session.prompt()
        if prompt_input == 'start':
            init.set_login_url()
        elif prompt_input == 'exit':
            break

    sys.exit(0)


if __name__ == '__main__':
    start_time = time.time()
    main()
    endtime_time = time.time()
    print(endtime_time-start_time)