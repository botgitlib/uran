from threading import Thread

def fff():
  return 2

x = Thread(target=fff)

x.start()
y = x.join()

print(y)

#a=[[]]

#a.insert(0,[])

#a[0].insert(0,"asd")
#a[0].insert(1,"qwe")

#a.insert(1,[])

#a[1].insert(0,"123")
#a[1].insert(1,"456")

#print(a[1][0])

