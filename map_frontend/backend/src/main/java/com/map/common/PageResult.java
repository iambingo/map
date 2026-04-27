package com.map.common;

import com.baomidou.mybatisplus.core.metadata.IPage;
import lombok.Getter;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 分页响应体
 */
@Getter
public class PageResult<T> implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    private final List<T> records;
    private final long total;
    private final long page;
    private final long size;
    private final long pages;

    private PageResult(List<T> records, long total, long page, long size, long pages) {
        this.records = records;
        this.total = total;
        this.page = page;
        this.size = size;
        this.pages = pages;
    }

    public static <T> PageResult<T> of(IPage<T> page) {
        return new PageResult<>(
                page.getRecords(),
                page.getTotal(),
                page.getCurrent(),
                page.getSize(),
                page.getPages()
        );
    }

    public static <T> PageResult<T> of(List<T> records, long total, long page, long size) {
        long pages = size == 0 ? 0 : (long) Math.ceil((double) total / size);
        return new PageResult<>(records, total, page, size, pages);
    }
}
