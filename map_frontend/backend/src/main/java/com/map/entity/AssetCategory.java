package com.map.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("asset_category")
public class AssetCategory extends BaseEntity {

    /** EQUITY | BOND | COMMODITY | REAL_ESTATE | CASH | ALTERNATIVE */
    private String code;
    private String name;
    private String nameEn;
    private String description;
    private String color;
    private String icon;
    private Boolean enabled;
}
