
package com.swarup.supplychain.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.HashMap;
import java.util.Map;

@Service
public class MLClientService {
    public Map callML(int delay, int demand, int weather) {
        RestTemplate restTemplate = new RestTemplate();
        String url = "http://127.0.0.1:8000/predict";

        Map<String, Object> request = new HashMap<>();
        request.put("delay", delay);
        request.put("demand_spike", demand);
        request.put("weather", weather);

        return restTemplate.postForObject(url, request, Map.class);
    }
}
