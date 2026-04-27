package com.map.controller;

import com.map.common.Result;
import com.map.entity.AssetCategory;
import com.map.mapper.AssetCategoryMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/assets")
@RequiredArgsConstructor
public class AssetController {

    private final AssetCategoryMapper assetCategoryMapper;

    @GetMapping("/categories")
    public Result<List<AssetCategory>> listCategories() {
        return Result.success(assetCategoryMapper.selectList(null));
    }

    @GetMapping("/categories/{id}")
    public Result<AssetCategory> getCategory(@PathVariable Long id) {
        AssetCategory category = assetCategoryMapper.selectById(id);
        if (category == null) {
            return Result.notFound("资产类别");
        }
        return Result.success(category);
    }

    @PostMapping("/categories")
    public Result<AssetCategory> createCategory(@RequestBody AssetCategory category) {
        assetCategoryMapper.insert(category);
        return Result.success(category);
    }

    @PutMapping("/categories/{id}")
    public Result<AssetCategory> updateCategory(@PathVariable Long id, @RequestBody AssetCategory category) {
        category.setId(id);
        assetCategoryMapper.updateById(category);
        return Result.success(category);
    }

    @DeleteMapping("/categories/{id}")
    public Result<Void> deleteCategory(@PathVariable Long id) {
        assetCategoryMapper.deleteById(id);
        return Result.success();
    }
}
