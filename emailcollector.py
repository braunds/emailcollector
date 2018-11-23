#!/usr/bin/env python3

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tempfile import NamedTemporaryFile
from string import ascii_letters
import os
import re
import sys
import csv
import random

try:
    import requests
except ImportError:
    print("You need to install requests library. You can use: pip install requests")
    sys.exit(1)



class EmailCollector():
    def __init__(self, root):
        self.current_proxies = {"http":"127.0.0.1", "https":"127.0.0.1"}
        self.addresses=[]
        self.headers={'user-agent':'letapogato/0.0.1'}
        self.timeout=10
        self.current_url=""
        self.root = root
        self.root.title('E-mail Collector')
        self.build_gui()
        self.init_gui()
        self.root.update()
        self.root.minsize(self.root.winfo_width()+100, root.winfo_height()+10)
        self.root.resizable(True, True)

    def build_gui(self):
        self.url_frame=Frame(self.root, bd=5, highlightbackground="black", highlightcolor="cyan", highlightthickness=1, width=100, height=100)
        Label(self.url_frame, text="URL:").pack()
        self.url_entry=Entry(self.url_frame)
        self.url_entry.pack(fill=X, expand=1)
        self.proxy_checkbutton=Checkbutton(self.url_frame, text="Using proxy", highlightcolor="yellow")
        self.proxy_checkbutton.pack()
        self.url_button=Button(self.url_frame, text="Collect", command=self.url_button_command, state=DISABLED)
        self.url_button.pack()
        self.url_frame.pack(pady=10, padx=5, fill=X, expand=1)
        
        self.proxy_frame=Frame(self.root, bd=5, highlightbackground="black", highlightcolor="cyan", highlightthickness=1, width=100, height=100)
        Label(self.proxy_frame, text="Proxy IP:PORT").pack()
        self.proxy_entry=Entry(self.proxy_frame, state=DISABLED)
        self.proxy_entry.pack()
        self.proxy_button=Button(self.proxy_frame, text="Check", state=DISABLED, command=self.proxy_button_command)
        self.proxy_button.pack()
        self.proxy_frame.pack(pady=10, padx=5, fill=X, expand=1)

        self.ip_frame=Frame(self.root, bd=5, highlightbackground="black", highlightcolor="cyan", highlightthickness=1, width=100, height=100)
        Label(self.ip_frame, text="See your current IP").pack()
        self.ip_label=Label(self.ip_frame, text="not checked yet", bg="black", fg="green")
        self.ip_label.pack()
        self.ip_button=Button(self.ip_frame, text="Check", command=self.ip_button_command)
        self.ip_button.pack()
        self.ip_frame.pack(pady=10, padx=5, fill=X, expand=1)

        self.email_frame=Frame(self.root)
        Label(self.email_frame, text="Collected emails:").pack()
        self.email_listbox=Listbox(self.email_frame, highlightcolor="cyan", highlightthickness=1)
        self.email_listbox.pack(fill=BOTH, expand=1, padx=5, pady=5)
        self.email_button=Button(self.email_frame, text="Save", state=DISABLED,command=self.email_button_command)
        self.email_button.pack()
        self.email_frame.pack(pady=10, fill=BOTH, expand=1)

    def init_gui(self):
        self.url_entry_var=StringVar()
        self.url_entry.configure(textvariable=self.url_entry_var)
        self.url_entry_var.trace("w", self.url_entry_modified_trace)
        self.proxy_checkbutton_var=IntVar()
        self.proxy_checkbutton.configure(variable=self.proxy_checkbutton_var, command=self.proxy_checkbutton_command)
        self.proxy_entry_var=StringVar()
        self.proxy_entry.configure(textvariable=self.proxy_entry_var)
        self.proxy_entry_var.trace("w", self.proxy_entry_modified_trace)
        

    def url_entry_modified_trace(self, name, index, mode, sv=""):
        if re.match("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", self.url_entry_var.get()):
            if self.proxy_checkbutton_var.get() == 1:
                if self.proxy_button.cget("fg") == "green":
                    self.url_button.configure(state=NORMAL)
            else:
                self.url_button.configure(state=NORMAL)
        else:
            self.url_button.configure(state=DISABLED)

    def proxy_checkbutton_command(self):
        if self.proxy_checkbutton_var.get() == 1:
            self.proxy_entry.configure(state=NORMAL)
            self.url_button.configure(state=DISABLED)
            if re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[:]([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$", self.proxy_entry_var.get()):
                self.proxy_button.configure(state=NORMAL)
        else:
            if re.match("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", self.url_entry_var.get()):
                self.url_button.configure(state=NORMAL)
            else:
                self.url_button.configure(state=DISABLED)
            self.proxy_entry.configure(state=DISABLED)
            self.proxy_button.configure(state=DISABLED)

    def url_button_command(self):
        self.email_listbox.delete(0, 'end')
        self.addresses.clear()
        if self.proxy_checkbutton_var.get() == 1:
            try:
                r=requests.get(self.url_entry_var.get(), proxies=self.current_proxies, timeout=self.timeout, headers=self.headers)
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Error", "This program cannot create a connection!\nProbably this sort of url address does not exist on internet!")
                self.email_button.configure(state=DISABLED)
                return
            except:
                messagebox.showerror("Error", f"A value of 'timeout' is set in this program. Current timeout value: {self.timeout} sec\n")    
                self.email_button.configure(state=DISABLED)
                return
            if not r.status_code == requests.codes.ok:
                messagebox.showerror("Http protocol error", f"Http Protocol error code:\n{r.status_code}")
                self.email_button.configure(state=DISABLED)
                return
        else:
            try:
                r=requests.get(self.url_entry_var.get(), timeout=self.timeout, headers=self.headers)
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Error", "This program cannot create a connection!\nProbably this sort of url address does not exist on internet!")
                self.email_button.configure(state=DISABLED)
                return
            except:
                messagebox.showerror("Error", f"A value of 'timeout' is set in this program. Current timeout value: {self.timeout} sec\n")    
                self.email_button.configure(state=DISABLED)
                return
            if not r.status_code == requests.codes.ok:
                messagebox.showerror("Http protocol error", f"Http Protocol error code:\n{r.status_code}")
                self.email_button.configure(state=DISABLED)
                return
        tmpfile=self.tmpfilename_generator()
        with open(tmpfile, "wt") as f:
            f.write(str(r.text.encode("utf-8")))
        del r
        with open(tmpfile) as f:
            for line in f:
                self.addresses+=re.findall(r'[\w\.-]+@[\w\.-]+', line)
                #print(line)
        os.remove(tmpfile)
        if not self.addresses:
            self.email_listbox.insert(0, "E-mails not found")
            self.email_button.configure(state=DISABLED)
        else:
            self.current_url=self.url_entry_var.get()
            self.addresses.sort()
            self.email_button.configure(state=NORMAL)
            for i,e in enumerate(set(self.addresses)):
                self.email_listbox.insert(i,e)
            


    def proxy_entry_modified_trace(self, name, index, mode, sv=""):
        self.url_button.configure(state=DISABLED)
        self.proxy_button.configure(text="Check", fg="black")
        if re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[:]([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$", self.proxy_entry_var.get()):
            self.proxy_button.configure(state=NORMAL)
        else:
            self.proxy_button.configure(state=DISABLED)

    def proxy_button_command(self):
        self.current_proxies['http']=self.proxy_entry_var.get()
        self.current_proxies['https']=self.proxy_entry_var.get()
        try:
            r=requests.get("https://httpbin.org/", proxies=self.current_proxies)
            self.proxy_button.configure(text="Good",fg='green')
            if re.match("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", self.url_entry_var.get()):
                self.url_button.configure(state=NORMAL)
            else:
                self.url_button.configure(state=DISABLED)
        except:
            self.url_button.configure(state=DISABLED)
            self.proxy_button.configure(text="Bad",fg='red')

    def ip_button_command(self):
        if self.proxy_checkbutton_var.get()==1:
            try:
                r=requests.get("http://httpbin.org/ip", proxies=self.current_proxies)
            except:
                self.ip_label.configure(text="couldn't check")
                return
        else:
            try:
                r=requests.get("http://httpbin.org/ip")
            except:
                self.ip_label.configure(text="couldn't check")
                return
        tmp=r.text.replace("\n", " ")
        del r
        current_ip=tmp.split('"') #[3]
        self.ip_label.configure(text=current_ip[3])
        

    def email_button_command(self):
        name=filedialog.asksaveasfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("text files","*.txt"),("csv files","*.csv"))) #errorpronous in windows, If i add defaultextension=".txt" then you will be able to use it on windows, too
        if name!=() and name!='':
            tmpadd=[self.current_url]
            tmpadd.extend(self.addresses)

        if name!=() and name!='' and re.match(".*\.txt$", name):
            with open(name, "w") as f:
                f.write("\n".join(tmpadd))
        elif name!=() and name!='':
            myFile=open(name, "w")
            with myFile:
                writer=csv.writer(myFile)
                writer.writerows(tmpadd)

    def tmpfilename_generator(self):
        letters=list(ascii_letters)
        random.shuffle(letters)
        return "{}{}".format("".join(letters), ".txt")
        
        
#########################################################
if __name__ == '__main__':
    root = Tk()
    EmailCollector(root)
    root.mainloop()
