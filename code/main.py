from flask import Flask
from flask_restx import Api, Resource, reqparse, Namespace
from module import convert, get_data, get_data_investing, country_output, group_output

app = Flask(__name__)
api = Api(app, version="1.0", title="VKSTOCKTRACK")

parser = reqparse.RequestParser()
parser.add_argument("ticker", required=True, type=str)
investing_parser = reqparse.RequestParser()
investing_parser.add_argument("ticker", required=True, type=str)
investing_parser.add_argument("url", required=True, type=str)

# '크롤링'과 '출력' 네임스페이스 생성
crawling_ns = Namespace("crawling", description="Crawling operations")
output_ns = Namespace("output", description="Output operations")

# 네임스페이스를 API에 추가
api.add_namespace(crawling_ns)
api.add_namespace(output_ns)


# '크롤링' 네임스페이스에 리소스 추가
@crawling_ns.route("/api/get_data")
@crawling_ns.doc(
    description="Crawl data and save as a CSV file with the ticker name. \nDescription : ^KS11, 055550.KS, VCB.VN"
)
class GetDataResource(Resource):
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        ticker_name = args["ticker"]
        result = get_data(ticker_name)
        return {"get_data": result.to_dict()}


@crawling_ns.route("/api/get_data_investing")
@crawling_ns.doc(
    description="Crawl from investing.com and save with the ticker name.\nNeed to enter the URL.\nURL : https://www.investing.com/indices/vn-historical-data \nTicker Name : ^VNINDEX.VN"
)
class GetDataInvestingResource(Resource):
    @api.expect(investing_parser)
    def get(self):
        args = investing_parser.parse_args()
        url = args["url"]
        ticker_name = args["ticker"]
        result = get_data_investing(url, ticker_name)
        return {"get_data_investing": result.to_dict()}


@output_ns.route("/api/country_output")
@output_ns.doc(
    description="Multiple outputs including previous close, today's open, today's volume, average volume, range of days, range of 52 weeks, MA 50, and MA 200.\nTicker Name : ^KS11, ^VNINDEX.VN"
)
class CountryOutputResource(Resource):
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        ticker = args["ticker"]
        result = country_output(ticker)
        return {"country_output": result}


@output_ns.route("/api/group_output")
@output_ns.doc(
    description="Multiple outputs including previous close, today's open, today's volume, average volume, range of days, range of 52 weeks, MA 50, MA 200, Beta, enterprise value, Buy and Sell.\nTicker Name : 055550.KS, VCB.VN"
)
class GroupOutputResource(Resource):
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        ticker = args["ticker"]
        result = group_output(ticker)
        return {"group_output": result}


if __name__ == "__main__":
    app.run(debug=True)
