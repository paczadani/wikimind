package com.rag.assistant.service;

import com.rag.assistant.dto.HealthResponse;
import com.rag.assistant.dto.QuestionRequest;
import com.rag.assistant.dto.RagResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;

@Service
public class RagBridgeService {

    private final RestTemplate restTemplate;
    private final String pythonBaseUrl;

    public RagBridgeService(RestTemplate restTemplate,
                            @Value("${python.service.base-url}") String pythonBaseUrl) {
        this.restTemplate = restTemplate;
        this.pythonBaseUrl = pythonBaseUrl;
    }

    public RagResponse ask(QuestionRequest request) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<QuestionRequest> entity = new HttpEntity<>(request, headers);
            return restTemplate.postForObject(pythonBaseUrl + "/ask-rag", entity, RagResponse.class);
        } catch (RestClientException e) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                    "Python RAG service is unavailable: " + e.getMessage(), e);
        }
    }

    @SuppressWarnings("unchecked")
    public HealthResponse checkHealth() {
        HealthResponse response = new HealthResponse();
        response.setSpringBootStatus("ok");
        try {
            Map<String, Object> pythonHealth = restTemplate.getForObject(
                    pythonBaseUrl + "/health", Map.class);
            response.setPythonServiceStatus("ok");
            if (pythonHealth != null) {
                response.setDbLoaded(Boolean.TRUE.equals(pythonHealth.get("db_loaded")));
                Object count = pythonHealth.get("chunk_count");
                response.setChunkCount(count instanceof Number n ? n.intValue() : 0);
            }
        } catch (RestClientException e) {
            response.setPythonServiceStatus("unreachable");
        }
        return response;
    }
}
