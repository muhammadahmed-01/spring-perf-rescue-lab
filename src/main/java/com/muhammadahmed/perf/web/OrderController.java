package com.muhammadahmed.perf.web;

import com.muhammadahmed.perf.dto.OrderSummaryDto;
import com.muhammadahmed.perf.dto.QueryStatsResponse;
import com.muhammadahmed.perf.service.OrderQueryService;
import com.muhammadahmed.perf.support.SqlStatementCounter;
import java.time.LocalDate;
import java.util.List;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderQueryService orderQueryService;
    private final SqlStatementCounter sqlStatementCounter;

    public OrderController(OrderQueryService orderQueryService, SqlStatementCounter sqlStatementCounter) {
        this.orderQueryService = orderQueryService;
        this.sqlStatementCounter = sqlStatementCounter;
    }

    @GetMapping("/buggy")
    public ResponseEntity<List<OrderSummaryDto>> getOrdersBuggy() {
        return okWithQueryCount("buggy", orderQueryService.listOrdersBuggy());
    }

    @GetMapping("/fixed")
    public ResponseEntity<List<OrderSummaryDto>> getOrdersFixed() {
        return okWithQueryCount("fixed", orderQueryService.listOrdersFixed());
    }

    @GetMapping("/stats/buggy")
    public QueryStatsResponse statsBuggy() {
        return orderQueryService.fetchOrdersBuggy();
    }

    @GetMapping("/stats/fixed")
    public QueryStatsResponse statsFixed() {
        return orderQueryService.fetchOrdersFixed();
    }

    @GetMapping("/search")
    public ResponseEntity<List<OrderSummaryDto>> searchOrders(
            @RequestParam(defaultValue = "fixed") String mode,
            @RequestParam(required = false) String customer,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate fromDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate toDate) {
        String normalizedMode = "buggy".equalsIgnoreCase(mode) ? "buggy" : "fixed";
        return okWithQueryCount(
                normalizedMode,
                orderQueryService.searchOrders(normalizedMode, customer, status, fromDate, toDate));
    }

    private ResponseEntity<List<OrderSummaryDto>> okWithQueryCount(String mode, List<OrderSummaryDto> orders) {
        return ResponseEntity.ok()
                .header("X-Query-Count", String.valueOf(sqlStatementCounter.getCount()))
                .header("X-Perf-Mode", mode)
                .body(orders);
    }
}
