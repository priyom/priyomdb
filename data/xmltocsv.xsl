<?xml version="1.0" encoding="utf-8" ?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no" />
    <xsl:template match="transmission">
        <xsl:text>"</xsl:text>
        <xsl:value-of select="ID" />
        <xsl:text>":"</xsl:text>
        <xsl:value-of select="BroadcastID" />
        <xsl:text>":"</xsl:text>
        <xsl:value-of select="ClassID" />
        <xsl:text>":"</xsl:text>
        <xsl:value-of select="Callsign[not(@lang)]" />
        <xsl:text>":"</xsl:text>
        <xsl:value-of select="Timestamp/@unix" />
        <xsl:text>":"</xsl:text>
        <xsl:value-of select="Recording" />
        <xsl:text>":"</xsl:text>
        <xsl:for-each select="Contents/group/item">
            <xsl:text>":"</xsl:text>
            <xsl:value-of select="." />
        </xsl:for-each>
        <xsl:text>"
</xsl:text>
    </xsl:template>
</xsl:stylesheet>
