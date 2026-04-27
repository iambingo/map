package com.map.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.map.common.PageResult;
import com.map.common.Result;
import com.map.entity.Portfolio;
import com.map.mapper.PortfolioMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/portfolios")
@RequiredArgsConstructor
public class PortfolioController {

    private final PortfolioMapper portfolioMapper;

    @GetMapping
    public Result<PageResult<Portfolio>> list(
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "20") long size
    ) {
        Page<Portfolio> p = portfolioMapper.selectPage(new Page<>(page, size), null);
        return Result.success(PageResult.of(p));
    }

    @GetMapping("/{id}")
    public Result<Portfolio> getById(@PathVariable Long id) {
        Portfolio portfolio = portfolioMapper.selectById(id);
        if (portfolio == null) {
            return Result.notFound("组合");
        }
        return Result.success(portfolio);
    }

    @PostMapping
    public Result<Portfolio> create(@RequestBody Portfolio portfolio) {
        portfolioMapper.insert(portfolio);
        return Result.success(portfolio);
    }

    @PutMapping("/{id}")
    public Result<Portfolio> update(@PathVariable Long id, @RequestBody Portfolio portfolio) {
        portfolio.setId(id);
        portfolioMapper.updateById(portfolio);
        return Result.success(portfolio);
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        portfolioMapper.deleteById(id);
        return Result.success();
    }
}
