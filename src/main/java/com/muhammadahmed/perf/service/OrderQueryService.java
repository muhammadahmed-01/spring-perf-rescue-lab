package com.muhammadahmed.perf.service;

import com.muhammadahmed.perf.domain.Order;
import com.muhammadahmed.perf.dto.OrderSummaryDto;
import com.muhammadahmed.perf.dto.QueryStatsResponse;
import com.muhammadahmed.perf.repository.OrderRepository;
import com.muhammadahmed.perf.support.SqlStatementCounter;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderQueryService {

    private final OrderRepository orderRepository;
    private final SqlStatementCounter sqlStatementCounter;

    public OrderQueryService(OrderRepository orderRepository, SqlStatementCounter sqlStatementCounter) {
        this.orderRepository = orderRepository;
        this.sqlStatementCounter = sqlStatementCounter;
    }

    @Transactional(readOnly = true)
    public QueryStatsResponse fetchOrdersBuggy() {
        sqlStatementCounter.reset();
        List<OrderSummaryDto> orders = loadBuggyOrders();
        return new QueryStatsResponse(sqlStatementCounter.getCount(), orders.size(), "buggy");
    }

    @Transactional(readOnly = true)
    public QueryStatsResponse fetchOrdersFixed() {
        sqlStatementCounter.reset();
        List<OrderSummaryDto> orders = loadFixedOrders();
        return new QueryStatsResponse(sqlStatementCounter.getCount(), orders.size(), "fixed");
    }

    @Transactional(readOnly = true)
    public List<OrderSummaryDto> listOrdersBuggy() {
        sqlStatementCounter.reset();
        return loadBuggyOrders();
    }

    @Transactional(readOnly = true)
    public List<OrderSummaryDto> listOrdersFixed() {
        sqlStatementCounter.reset();
        return loadFixedOrders();
    }

    @Transactional(readOnly = true)
    public List<OrderSummaryDto> searchOrders(
            String mode, String customer, String status, LocalDate fromDate, LocalDate toDate) {
        sqlStatementCounter.reset();
        List<OrderSummaryDto> orders = "fixed".equalsIgnoreCase(mode) ? loadFixedOrders() : loadBuggyOrders();
        return orders.stream()
                .filter(order -> matchesCustomer(order, customer))
                .filter(order -> matchesStatus(order, status))
                .filter(order -> matchesFromDate(order, fromDate))
                .filter(order -> matchesToDate(order, toDate))
                .toList();
    }

    private boolean matchesCustomer(OrderSummaryDto order, String customer) {
        if (customer == null || customer.isBlank()) {
            return true;
        }
        return order.customerName().toLowerCase().contains(customer.toLowerCase());
    }

    private boolean matchesStatus(OrderSummaryDto order, String status) {
        if (status == null || status.isBlank()) {
            return true;
        }
        return status.equalsIgnoreCase(order.status());
    }

    private boolean matchesFromDate(OrderSummaryDto order, LocalDate fromDate) {
        if (fromDate == null) {
            return true;
        }
        Instant start = fromDate.atStartOfDay().toInstant(ZoneOffset.UTC);
        return !order.createdAt().isBefore(start);
    }

    private boolean matchesToDate(OrderSummaryDto order, LocalDate toDate) {
        if (toDate == null) {
            return true;
        }
        Instant end = toDate.plusDays(1).atStartOfDay().toInstant(ZoneOffset.UTC);
        return order.createdAt().isBefore(end);
    }

    private List<OrderSummaryDto> loadBuggyOrders() {
        return orderRepository.findAll().stream()
                .map(this::mapOrderWithLazyLoads)
                .toList();
    }

    private List<OrderSummaryDto> loadFixedOrders() {
        return orderRepository.findAllOrdersWithItemsAndUser().stream()
                .map(this::mapOrder)
                .toList();
    }

    private OrderSummaryDto mapOrderWithLazyLoads(Order order) {
        // Intentional N+1: lazy user and items fire separate SELECTs per order.
        return mapOrder(order);
    }

    private OrderSummaryDto mapOrder(Order order) {
        String customerName = order.getUser().getName();
        List<OrderSummaryDto.OrderItemDto> items = order.getItems().stream()
                .map(item -> new OrderSummaryDto.OrderItemDto(
                        item.getProductName(),
                        item.getQuantity(),
                        item.getUnitPrice()))
                .toList();
        return toSummary(order, customerName, items);
    }

    private OrderSummaryDto toSummary(
            Order order,
            String customerName,
            List<OrderSummaryDto.OrderItemDto> items) {
        BigDecimal total = items.stream()
                .map(item -> item.unitPrice().multiply(BigDecimal.valueOf(item.quantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        return new OrderSummaryDto(
                order.getId(),
                customerName,
                order.getStatus(),
                order.getCreatedAt(),
                items.size(),
                total,
                items);
    }
}
