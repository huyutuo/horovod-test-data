
# 在每个文件夹路径下修改对应的filename，然后执行以下命令
filename=12-10-09-resnet50-fusion128-cycle20
allrank_name=""$filename"-allrank"
rank_0_name=""$filename"-rank_0"
rank_1_name=""$filename"-rank_1"
rank_2_name=""$filename"-rank_2"
rank_3_name=""$filename"-rank_3"
cat $filename | grep  "iietest" > $allrank_name
cat $allrank_name | grep  -F "[1,0]" > $rank_0_name
cat $allrank_name | grep  -F "[1,1]" > $rank_1_name
cat $allrank_name | grep  -F "[1,2]" > $rank_2_name
cat $allrank_name | grep  -F "[1,3]" > $rank_3_name