package com.rag.assistant.controller;

import com.rag.assistant.dto.HealthResponse;
import com.rag.assistant.dto.QuestionRequest;
import com.rag.assistant.dto.RagResponse;
import com.rag.assistant.service.RagBridgeService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
public class RagController {

    private final RagBridgeService ragBridgeService;

    public RagController(RagBridgeService ragBridgeService) {
        this.ragBridgeService = ragBridgeService;
    }

    @PostMapping("/ask")
    public ResponseEntity<RagResponse> ask(@Valid @RequestBody QuestionRequest request) {
        return ResponseEntity.ok(ragBridgeService.ask(request));
    }

    @GetMapping("/health")
    public ResponseEntity<HealthResponse> health() {
        return ResponseEntity.ok(ragBridgeService.checkHealth());
    }
}
