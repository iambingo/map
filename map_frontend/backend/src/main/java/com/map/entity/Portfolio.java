package com.map.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;

@Getter
@Setter
@TableName("portfolio")
public class Portfolio extends BaseEntity {

    private String name;
    private String code;
    private String description;
    private String benchmarkCode;
    private String benchmarkName;
    private BigDecimal totalValue;
    private String currency;
    private LocalDate inceptionDate;
    private String status;      // ACTIVE | INACTIVE | CLOSED
    private Long managerId;
}
