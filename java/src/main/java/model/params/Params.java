package model.params;

public abstract class Params {

    public Params() {
    }

    public Params(String channelType, String symbol) {
        this.channelType = channelType;
        this.symbol = symbol;
    }

    private String channelType;
    private String symbol;

    public String getChannelType() {
        return channelType;
    }

    public void setChannelType(String channelType) {
        this.channelType = channelType;
    }

    public String getSymbol() {
        return symbol;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    @Override
    public String toString() {
        return "channelType='" + channelType + '\'' +
                ", symbol='" + symbol + '\'';
    }
}
