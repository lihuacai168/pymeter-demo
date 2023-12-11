"""unittest module"""
from typing import Any
from unittest import TestCase, main

from pymeter.api.assertions import ResponseAssertion
from pymeter.api.config import (
    TestPlan,
    ThreadGroupSimple,
    ThreadGroupWithRampUpAndHold,
    Vars,
)
from pymeter.api.postprocessors import JsonExtractor
from pymeter.api.reporters import HtmlReporter
from pymeter.api.samplers import DummySampler, HttpSampler
from pymeter.api.timers import ConstantTimer, UniformRandomTimer


class TestTestPlanClass(TestCase):
    def test_1(self: Any) -> None:
        # 创建一个JsonExtractor对象,参数分别是"variable"和"args.var"
        json_extractor: JsonExtractor = JsonExtractor("variable", "args.var")

        # 创建一个均匀随机计时器，时间间隔在1000至2000毫秒之间
        timer: UniformRandomTimer = UniformRandomTimer(1000, 2000)

        ra: ResponseAssertion = ResponseAssertion().contains_substrings("var")
        # 创建一个HttpSampler对象，用于发送HTTP请求并记录响应
        http_sampler: HttpSampler = HttpSampler(
            "Echo",
            "http://119.91.147.215:18080/get?var=${__Random(0,10)}",
            timer,
            json_extractor,
            ra
        )

        # 创建一个DummySampler对象，仅用于模拟一些操作，不实际执行任何网络请求
        dummy_sampler: DummySampler = DummySampler("dummy ${variable}", "hi dummy")

        # 创建一个线程组，其中包含10个线程，每个线程的运行时间为1秒，整个线程组的持续时间为60秒
        tg: ThreadGroupWithRampUpAndHold = ThreadGroupWithRampUpAndHold(
            100, 3, 60, http_sampler, dummy_sampler, name="Some Name"
        )

        # 创建一个HTML报告生成器
        html_reporter: HtmlReporter = HtmlReporter()

        # 创建一个测试计划，其中包含tg线程组和html_reporter报告生成器
        tp: TestPlan = TestPlan(tg, html_reporter)

        # 运行测试计划，返回统计数据
        stats = tp.run()

        # 打印测试的统计數據
        print(
            f"duration= {stats.duration_milliseconds}",
            f"mean= {stats.sample_time_mean_milliseconds}",
            f"min= {stats.sample_time_min_milliseconds}",
            f"median= {stats.sample_time_median_milliseconds}",
            f"90p= {stats.sample_time_90_percentile_milliseconds}",
            f"95p= {stats.sample_time_95_percentile_milliseconds}",
            f"99p= {stats.sample_time_99_percentile_milliseconds}",
            f"max= {stats.sample_time_max_milliseconds}",
            sep="\t",
        )

        # 断言99%分位数的样本时间小于2000毫秒
        self.assertLess(stats.sample_time_99_percentile_milliseconds, 2000)

    def test_vars(self):
        # 创建JMeter变量
        jmeter_variables = Vars(id1="value1")
        # 除了直接初始化，也能通过set，设置JMeter变量
        jmeter_variables.set("id2", "value2")
        timer = ConstantTimer(1000)

        http_sampler1 = HttpSampler(
            "Echo_${id1}", "https://postman-echo.com/get?var=${id1}", timer
        )
        thread_group1 = ThreadGroupSimple(3, 10)
        thread_group1.children(http_sampler1)

        http_sampler2 = HttpSampler(
            "Echo_${id2}", "https://postman-echo.com/get?var=do", timer
        )
        thread_group2 = ThreadGroupSimple(3, 10, http_sampler2)

        html_reporter = HtmlReporter()
        test_plan = TestPlan(
            thread_group1, thread_group2, html_reporter, jmeter_variables
        )
        stats = test_plan.run()

        # 打印测试的统计數據
        print(
            f"duration= {stats.duration_milliseconds}",
            f"mean= {stats.sample_time_mean_milliseconds}",
            f"min= {stats.sample_time_min_milliseconds}",
            f"median= {stats.sample_time_median_milliseconds}",
            f"90p= {stats.sample_time_90_percentile_milliseconds}",
            f"95p= {stats.sample_time_95_percentile_milliseconds}",
            f"99p= {stats.sample_time_99_percentile_milliseconds}",
            f"max= {stats.sample_time_max_milliseconds}",
            sep="\t",
        )


if __name__ == "__main__":
    main()
