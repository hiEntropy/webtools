import urllib3
import sys
import os
from bs4 import BeautifulSoup

'''
Simple method to return connection data about a host.
'''
def getHTML(path):
    try:
        headers = urllib3.make_headers(keep_alive=True,user_agent="Microsoft-Windows/6.3 UPnP/1.0")
        http=urllib3.PoolManager(timeout=3.0)
        connection=http.request('get',path,headers=headers)
        return connection
    except:
        return None

def connectionMessages(connection):
    if connection!=None:
        status=connection.status
        if status==200:
            print("Connection Established")
            return True
        elif status == 204:
            print("No Content")
            return False;
        elif status >299 and status<400:
            print("Being Redirected")
            return True;
        elif status>399:
            print("Connection NOT Established "+str(status))
            return False
        else:
            print("Connection NOT Established "+str(connection))
            return False
    else:
        print("Connection Not Established: Connection equals None")
        return False
'''
requires an array to be passed as the argument
'''
def makeLower(array):
    for x in range(0,len(array)):
        array[x]=array[x].lower()

def writeToFile(content,location):
    with open(location,'wb') as out:                            
        out.write(content)
    print("Success")


'''
Focusses on links to JavaScript sources and returns a list of them.
<link>, <a> and <script> tags are inspected for Javascipt links
Br3@d1986
'''
def getJSLinks(target):
    connection=getHTML(target)
    if connectionMessages(connection):
        html= connection.data
        soupObject=BeautifulSoup(html,'html.parser')
        linkTags=soupObject.find_all(name=['link','a'])
        scriptTags=soupObject.find_all(name="script")
        scriptTags.extend(soupObject.find_all(name="head",attr="script"))
        jsLinks=[]
        for x in linkTags:
            link=x.get('href').split(".")
            tag=link[len(link)-1]
            if tag=="js":
                jsLinks.append(x.get('href'))
        for x in scriptTags:
            src=x.get("src")
            if src!=None:
                jsLinks.append(src)
        return jsLinks

def getGifLinks(target):
    connection=getHTML(target)
    if connectionMessages(connection):
        html= connection.data
        soupObject=BeautifulSoup(html,'html.parser')
        linkTags=soupObject.find_all(['link','a'])
        imgTags=soupObject.find_all('img')
        gifLinks=[]
        for x in linkTags:
            link=x.get('href')
            if link!=None:
                link=link.split(".")
                tag=link[len(link)-1]
            if tag=="gif":
                gifLinks.append(x.get('href'))
        for x in imgTags:            
            link=x.get("src")
            if link!=None:
                link=link.split(".")
                tag=link[len(link)-1]
            if tag=="gif":
                gifLinks.append(x.get('src'))
        return gifLinks

'''
This returns all JavaScript code that is written in an HTML webpage.
This will ignore links and focus on local code only.
'''
def getJS(target):
    connection=getHTML(target)
    if connectionMessages(connection):
        html=connection.data
        soupObject=BeautifulSoup(html,'html.parser')
        scriptTags=soupObject.find_all(name="script")
        jsCode=[]
        for x in scriptTags:
            src=x.get("src")
            if src==None:
                jsCode.append(src)
        return jsCode

def getHiddenFields(target):
    connection= getHTML(target)
    results= [];
    if connectionMessages(connection):
        html=connection.data
        soupObject = BeautifulSoup(html,'html.parser')
        inputs = soupObject.find_all(attrs={"type":"hidden"})
        for x in inputs:
            if(x.value != None):
                results.add(resutlts.value);
        return results
        


'''
Returns the file name from a URL
'''
def grabFileName(url):
    splitUrl=url.split("/")
    return splitUrl[len(splitUrl)-1]

'''
Returns the domain name from a URL
'''
def grabDomainName(url):
    splitUrl=url.split("/")
    return splitUrl[3]


'''
WORKING HERE

this will write an array to a new file
'''
def arrayToFile(array,name,extention):
    filename=assignFilename(name,extention)
    text=""
    for x in array:
        text+=x+"\n\n"
    with open(filename,'a') as out:                            
        out.write(text)        
    print("Successful write: "+os.getcwd()+"\\"+filename)

'''
Needs to be tested

Checks to see if a file exists and increments a count to get
a unique file name
'''
def assignFilename(fileName,extention):
    name=fileName
    count=1
    while(os.path.isfile(name+extention)):
          name=fileName+str(count)
          count+=1
          name=fileName
    return fileName+"("+str(count)+")"+extention


'''
Downloads the target file to disk
'''
def downloadFile(fileLocation):
    try:
        http=urllib3.PoolManager()
        connection=http.request('GET',fileLocation)
        with open(grabFileName(fileLocation),'wb') as out:                            
            out.write(connection.data)
        print("Success")
    except:
        print("Failure")
        return False
# args[path,command,target,-s,fileSaveLocation]
def main():
    args=sys.argv
    if len(args)>1 :
        makeLower(args)
        command=args[1]
        target=args[2]
        print(args)
        #print ("length args "+str(len(args)))
        
        if command=="html":
            print("Getting html for "+target)
            html=getHTML(target).data
            soupObject=BeautifulSoup(html,'html.parser')
            text=soupObject.prettify().encode('UTF-8')
            if len(args)>=5 and args[3] == "-s":
                writeToFile(text,args[4]+"\\"+target+".txt")
            elif len(args)>=4 and args[3] == "-s":
                print("Writing to "+target+".txt")
                writeToFile(text,os.getcwd()+"\\"+target+".txt")
            else:
                print(text)
        elif command=="save":
            print("Saving to local drive")
            downloadFile(target)               
        elif command=="js":
            results=getJSLinks(target)
            if results:
                fileName=grabFileName(target)
                arrayToFile(results,fileName,".js")
            if results and len(args)>3 and args[3]=="-s":
                for x in results:
                    downloadFile(x)
                    print(x+" saved") 
            else:
                print("No javascript sources found")
        elif command=="gif":
            links=getGifLinks(target)
            for x in links:
                downloadFile(x)
        elif command=="hidden":
            getHiddenFields(target)
        else:
            print("Invalid Command: "+command+"\n Valid Commands Are:\n html \n save \n js")
    else:
        print("Please use a command \n Valid Commands Are:\n\n html \n save \n js")

main()
