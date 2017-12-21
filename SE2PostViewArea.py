from bs4 import BeautifulSoup
from urllib import request
import requests
import urllib
import re


class SE2PostViewArea:
    def __init__(self, postViewArea):
        self.postViewArea = str(postViewArea)
        self.header = self.getHeader()
        self.paragraphs = self.getParagraphs()
        self.footer = self.getFooter()

    def writeSE2PostToFile(self, crawler):
        crawler.backupFile.write("\n")
        crawler.backupFile.write(self.header)
        for p in self.paragraphs:
            crawler.backupFile.write("\n")
            crawler.backupFile.write(p.paragraph)
        crawler.backupFile.write("\n")
        crawler.backupFile.write(self.footer)

    def getHeader(self):
        header = ""
        try:
            header = re.search("<div.*?><p", self.postViewArea, re.DOTALL | re.MULTILINE).group()
            header = header[:len(header)-2]
        except:
            header = " "
        return header

    def getFooter(self):
        footer = re.search("</div>*", self.postViewArea).group()
        return footer

    def getParagraphs(self):
        tags = None
        pTags = re.findall("<p.+?</p>", self.postViewArea, re.DOTALL)
        if len(pTags) < 1:
            divTags = re.findall("<div.+?</div>", self.postViewArea, re.DOTALL)
            tags = divTags
        else:
            tags = pTags
        paragraphs = []
        for tag in tags:
            paragraphs.append(SE2Paragraph(str(tag)))
        return paragraphs

    def handleParagraphs(self, crawler):
        print("[", end=' ')
        for p in self.paragraphs:
            if p.isImageInParagraph():
                print("Img", end=' ')
                imgUrl = p.getImageUrlInParagraph()
                imgSaveName = crawler.getSaveImageName(imgUrl)
                p.saveImageInArea(crawler.backupDir, imgSaveName)
                print(": " + imgSaveName, end=', ')
                p.replaceImgSrcTag(imgSaveName)
                crawler.imageCount += 1
            else:
                print(".", end=' ')
        print("]", end=' ')

class SE2Paragraph:
    def __init__(self, rawParagraph):
        self.paragraph = str(rawParagraph)

    def isImageInParagraph(self):
        if "class=\"_photoImage\"" in self.paragraph:
            return True
        else:
            return False

    def getImageUrlInParagraph(self):
        imgSrcRegularExpr = re.compile("src=\".*?\"")
        imgSrc = imgSrcRegularExpr.search(self.paragraph).group()
        imgUrl = re.sub("src=", '', imgSrc)
        imgUrl = re.sub("\"", '', imgUrl)
        if self.isDoubleQuotedSrc(imgUrl):
            imgUrl = self.getImgUrlInQuotedUrl(imgUrl)
        imgUrl = urllib.request.quote(imgUrl.encode('utf-8'), ':?=/')
        return imgUrl

    def replaceImgSrcTag(self, imgSaveName):
        imgSrcRegularExpr = re.compile("src=\"http.*?\"")
        self.paragraph = imgSrcRegularExpr.sub("src=\"" + imgSaveName + "\"", self.paragraph)

    def saveImageInArea(self, backupDir, imgSaveName):
        if self.isImageInParagraph():
            imageUrl = self.getImageUrlInParagraph()
            try:
                request.urlretrieve(imageUrl, "./" + backupDir + "/" + imgSaveName)
            except urllib.error.HTTPError:
                print("ERROR in image URL")

    def isDoubleQuotedSrc(self, imgUrl):
        if "%22http%3A%2F%2F" in imgUrl:
            return True
        else:
            return False

    def getImgUrlInQuotedUrl(self, quotedUrl):
        print("doubleQ" + quotedUrl)
        quotedImgUrlRegularExpr = re.compile("http\%3A\%2F\%2F.*?(gif|jpg|png)")
        imageUrl = quotedImgUrlRegularExpr.search(quotedUrl).group()
        imageUrl = urllib.request.unquote(imageUrl, encoding='utf-8')
        return imageUrl
