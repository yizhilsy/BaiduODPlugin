一、插件功能
本插件实现了PP-ChatOCR的部分功能，针对文本图像输入实现以下功能：
1.上传一张图像，提取图像中的文本信息。
2.可以进一步对输出结果进行关键信息抽取，其中关键字段包含在【】或者[]里面。
3.可以将图像进行表格html格式转换。


二、插件上线
先安装requirements.txt依赖包（python版本要求大于3.10），然后运行python demo_server.py启动服务，之后按文心一言插件流程上线文心一言平台

三、插件功能测试用例
触发该插件，用户请求中需要包含抽取图像文字和地址，或者抽取表格图像和地址等信息。

1.请抽取图像中文字 <url>https://img1.baidu.com/it/u=3839173349,850651411&fm=253&fmt=auto&app=138&f=JPEG?w=889&h=500<\url>

2.请抽取图像中文字，<url>https://img0.baidu.com/it/u=734673557,2609043629&fm=253&fmt=auto&app=138&f=JPEG?w=600&h=384<\url>

3.请抽取图像中始发站、终点站、车次和票价，<url>https://img0.baidu.com/it/u=734673557,2609043629&fm=253&fmt=auto&app=138&f=JPEG?w=600&h=384<\url>

4.请对下面表格图像进行文本化，<url>https://edu-tiku.cdn.bcebos.com/originalpic/59117799c043278166b086b68a9910a8.jpg?authorization=bce-auth-v1/ceae51ce68104d68be6f9ad6f91bceee/2021-09-26T18:31:43Z/630720000//4e76901228cfe4d78c7dfe4968096a6d761e708aed4fe94b4f42dd735b7994b4<\url>

5.请抽取表格图像中AC路段距离，<url>https://edu-tiku.cdn.bcebos.com/originalpic/59117799c043278166b086b68a9910a8.jpg?authorization=bce-auth-v1/ceae51ce68104d68be6f9ad6f91bceee/2021-09-26T18:31:43Z/630720000//4e76901228cfe4d78c7dfe4968096a6d761e708aed4fe94b4f42dd735b7994b4<\url>

三、更多
1.关于PP-ChatOCR更多的优化，请参考PP-ChatOCR在星河社区的项目 https://aistudio.baidu.com/projectdetail/6488689

