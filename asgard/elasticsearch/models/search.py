from pydantic import BaseModel


class AggregationItem(BaseModel):
    value: float


class AggregationAppsStatsResult(BaseModel):
    avg_cpu_pct: AggregationItem
    avg_cpu_thr_pct: AggregationItem
    avg_mem_pct: AggregationItem


class AppsStatsResult(BaseModel):
    aggregations: AggregationAppsStatsResult
