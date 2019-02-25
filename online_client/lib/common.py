def show_process(percent, width=50):
    msg = '[%%-%ds]' % width % ('>' * int(percent * width))
    print('\r' + msg + '进度:%.2f%%' % (percent * 100), end='')
