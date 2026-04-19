package com.rag.assistant.dto;

public class HealthResponse {

    private String springBootStatus;
    private String pythonServiceStatus;
    private boolean dbLoaded;
    private int chunkCount;

    public String getSpringBootStatus() { return springBootStatus; }
    public void setSpringBootStatus(String s) { this.springBootStatus = s; }

    public String getPythonServiceStatus() { return pythonServiceStatus; }
    public void setPythonServiceStatus(String s) { this.pythonServiceStatus = s; }

    public boolean isDbLoaded() { return dbLoaded; }
    public void setDbLoaded(boolean b) { this.dbLoaded = b; }

    public int getChunkCount() { return chunkCount; }
    public void setChunkCount(int n) { this.chunkCount = n; }
}
