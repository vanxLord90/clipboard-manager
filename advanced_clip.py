from tkinter import Tk, Frame, BOTH, Menu, TclError, Label, RAISED, SUNKEN, SOLID, messagebox
import pyperclip

class ClipAdvanced(Frame):
    def __init__(self, parent=None):
        self.parent = parent

        Frame.__init__(self, parent, height=600, width=600)
        parent.title("Clipboard Manager")
        parent.resizable(False, False)
        self.pack_propagate(0)
        self.pack()

        self.initDefaultValues()
        self.pollingFrequencyMs = 100
        self.truncateTextLength = 100
        self.maxClippingsOnApp = 10
        self.labelArray = []
        self.debug = False

        self.initMenu()

    def initDefaultValues(self):
        self.clipboardContent = set()
        self.clipboardContentMapping = {}
        self.labelUpdateVal = 0

    def createLayout(self):
        for i in range(self.maxClippingsOnApp):
            l = Label(self, text="", cursor="plus", relief=RAISED, pady=5,  wraplength=500)
            l.pack(fill=BOTH, padx=5, pady=2, expand=1)
            l.bind("<Button-1>", lambda e, labelNum=i: self.onClick(labelNum))
            l.bind("<Button-3>", self.onLabelRightClick)
            self.labelArray.append({
                "label": l,
                "text": "", #only for debugging purposes, only label["text"] matters
                "clickCount": 0,
                "updated": 0,
            })

    def updateClipboard(self):
            try:
                #cliptext = self.clipboard_get()
                cliptext = pyperclip.paste()
                self.processClipping(cliptext=cliptext)

            except Exception as e:
                print("ERROR!! -> ", e)

            if self.debug:
                self.after(ms=5000, func=self.updateClipboard)
            else:
                self.after(ms=self.pollingFrequencyMs, func=self.updateClipboard)

    def cleanClipText(self, cliptext):
        #Removing all characters > 65535 (that's the range for tcl)
        cliptext = "".join([c for c in cliptext if ord(c) <= 65535])
        #Clipping content to look pretty
        if len(cliptext) > self.truncateTextLength:
            cliptextShort = cliptext[:self.truncateTextLength]+" ..."
        else:
            cliptextShort = cliptext
        #Removing new lines from short text
        cliptextShort = cliptextShort.replace("\n", "").strip()
        return (cliptext, cliptextShort)

    def initMenu(self):
        menubar = Menu(self)
        optionsMenu = Menu(menubar, tearoff=0)
        optionsMenu.add_checkbutton(label="Always on top", command=self.toggle_on_top)
        optionsMenu.add_command(label="Clear all (except last)", command=self.clear)
        optionsMenu.add_command(label="Clear individual", command=self.clearOne)
        self.labelContextMenu= Menu(self, tearoff=0)
        self.labelContextMenu.add_command(label="Clear One", command = lambda: self.clearOne(self.activeLabel))
        menubar.add_cascade(label="Options", menu=optionsMenu)
        self.parent.config(menu=menubar)

    def setupLabels(self):
        for i, labelElm in enumerate(self.labelArray):
            label = labelElm['label']
            label.bind("<Button-3>", self.onLabelRightClick)

    def onLabelRightClick(self, event):
        """Handle right-click on a label to show the context menu."""
        self.activeLabel = self.getLabelNumFromEvent(event)
        if self.activeLabel is not None:
            self.labelContextMenu.post(event.x_root, event.y_root)
        else:
            print("Could not find label from event")

    def getLabelNumFromEvent(self, event):
        """Extract label number from event."""
        for num, labelElm in enumerate(self.labelArray):
            if labelElm['label'] == event.widget:
                return num
        return None  # In case nothing matches

    # toggle always on top
    def toggle_on_top(self):
        if self.parent.attributes("-topmost") == 0:
            self.parent.attributes("-topmost", 1)
        else:
            self.parent.attributes("-topmost", 0)

    # clear all
    def clear(self):
        result = messagebox.askyesno("Clear Everything","Sure?")
        if result:
            for labelElm in self.labelArray:
                labelElm["label"]["text"]=""
                labelElm["label"]["relief"]=RAISED
                labelElm["text"] = ""
                labelElm["clickCount"]=0
                labelElm["updated"]=0
            self.initDefaultValues()
    # onclick
    def clearOne(self,labelNum):
        labelElm = self.labelArray[labelNum]
        if messagebox.askyesno("ClearOne","Clear this item?"):
            label = labelElm["label"]
            label["text"]=""
            label["relief"] = RAISED
            labelElm["clickCount"] = 0
            labelElm["updated"] = 0
            if self.debug:
                print(f"Cleared content for label {labelNum}")

    def onClick(self, labelNum):
        labelElm = self.labelArray[labelNum]
        label = labelElm["label"]
        if label["text"] == "":
            return
        if self.debug:
            print(labelElm)
            print("copied ", self.clipboardContentMapping[label["text"]])
        pyperclip.copy(self.clipboardContentMapping[label["text"]])
        label["relief"] = SUNKEN
        labelElm["clickCount"] = 1
        self.after(ms=100, func=lambda label=label: self.emphasizeClick(label))

    # animate click
    def emphasizeClick(self, label):
        label["relief"]=SOLID
    # process clipping
    def processClipping(self, cliptext):
        if self.debug:
            print("Called function, got ->", cliptext)

        cliptext, cliptextShort = self.cleanClipText(cliptext=cliptext)
        #Update screen if new copies found
        if cliptext not in self.clipboardContent and cliptextShort:

            if cliptextShort not in self.clipboardContentMapping:
                self.labelUpdateVal += 1
                labelArrsortByUpdated = sorted(self.labelArray, key=lambda t:t["updated"])
                labelArrsortByClicked = sorted(labelArrsortByUpdated, key=lambda t:t["clickCount"])

                labelElem = labelArrsortByClicked[0]
                label = labelElem["label"]
                labelText = label["text"]
                if labelText in self.clipboardContentMapping:
                    self.clipboardContent.discard(self.clipboardContentMapping[labelText])
                    self.clipboardContentMapping.pop(labelText)
                label["text"] = cliptextShort
                label["relief"] = RAISED
                labelElem["updated"] = self.labelUpdateVal
                labelElem["text"] = cliptextShort
                labelElem["clickCount"] = 0
            else: # New clipping but shortened version is the same, so discard previous value
                self.clipboardContent.discard(self.clipboardContentMapping[cliptextShort])

            self.clipboardContent.add(cliptext)
            self.clipboardContentMapping[cliptextShort] = cliptext

            self.update()
            self.parent.update()
            self.pack()

if __name__ == '__main__':
    root = Tk()
    Clippy = ClipAdvanced(root)
    Clippy.createLayout()
    Clippy.updateClipboard()
    Clippy.mainloop()