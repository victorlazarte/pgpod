<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
    <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>Paul Graham Essays Podcast</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { color: #333; }
                    .episode { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                    .title { font-size: 1.5em; color: #0066cc; margin-bottom: 10px; }
                    .description { margin: 10px 0; }
                    .pubDate { color: #666; font-size: 0.9em; }
                    .audio { margin-top: 10px; }
                </style>
            </head>
            <body>
                <h1><xsl:value-of select="rss/channel/title"/></h1>
                <p><xsl:value-of select="rss/channel/description"/></p>
                <xsl:for-each select="rss/channel/item">
                    <div class="episode">
                        <div class="title"><xsl:value-of select="title"/></div>
                        <div class="description"><xsl:value-of select="description"/></div>
                        <div class="pubDate">Published: <xsl:value-of select="pubDate"/></div>
                        <div class="audio">
                            <audio controls>
                                <source src="{enclosure/@url}" type="audio/mpeg"/>
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    </div>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet> 