from flask import Flask


def test(app:Flask):
    
    @app.route('/test', methods = ['GET'])
    def test_site():
        return "hello world"
    
    
if __name__ == "__main__":
    app = Flask(__name__)
    test(app)