from tkinter import Tk,Label,RAISED
import pyperclip

def updateClipboard():
    cliptext = pyperclip.paste()
    processClip(cliptext)
    root.after(ms=1000,func=updateClipboard)

def cleanClipText(cliptext):
    cliptext2 = "".join([c for c in cliptext if ord(c)<=65535])
    return cliptext2

def processClip(cliptext):
    cliptextCleaned = cleanClipText(cliptext=cliptext)
    label["text"] = cliptextCleaned

def onClick(labelElm):
    labelT= labelElm["text"]
    print(labelT)
    pyperclip.copy(labelT)


if __name__=='__main__':
    root = Tk()
    label = Label(root, text="Copy", cursor="plus", relief=RAISED, pady=5, wraplength=500)
    label.bind("<Button-1>",lambda event, labelElm=label: onClick(labelElm))
    label.pack()
    updateClipboard()
    root.mainloop()
