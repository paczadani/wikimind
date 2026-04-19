package com.rag.assistant.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class QuestionRequest {

    @NotBlank(message = "question must not be blank")
    @Size(min = 3, message = "question must be at least 3 characters")
    private String question;

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
}
