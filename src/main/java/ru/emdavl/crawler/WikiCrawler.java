package ru.emdavl.crawler;

import edu.uci.ics.crawler4j.crawler.Page;
import edu.uci.ics.crawler4j.crawler.WebCrawler;
import edu.uci.ics.crawler4j.parser.HtmlParseData;
import edu.uci.ics.crawler4j.url.WebURL;
import lombok.SneakyThrows;

import java.io.FileWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;

public class WikiCrawler extends WebCrawler {
    private final static Pattern FILTERS = Pattern.compile(".*(\\.(css|js|gif|jpg"
            + "|png|mp3|mp4|zip|gz|svg))$");
    private static AtomicInteger cnt = new AtomicInteger(0);
    private ConcurrentHashMap<String, String> filesMap;

    public WikiCrawler(ConcurrentHashMap<String, String> filesMap) {
        this.filesMap = filesMap;
    }

    @Override
    public boolean shouldVisit(Page referringPage, WebURL url) {
        String href = url.getURL().toLowerCase();
        return !FILTERS.matcher(href).matches()
                && href.startsWith("https://ru.wikipedia.org/wiki");
    }

    @SneakyThrows
    @Override
    public void visit(Page page) {
        String url = page.getWebURL().getURL();

        if (page.getParseData() instanceof HtmlParseData) {
            HtmlParseData htmlParseData = (HtmlParseData) page.getParseData();
            String html = htmlParseData.getHtml();
            Integer indx = cnt.getAndIncrement();
            String filePath = "/Users/e.davlyatov/IdeaProjects/mvn-sandbox/src/main/resources/crawled/" + indx + ".html";
            Path file = Files.createFile(Path.of(filePath));
            try (var writer = new FileWriter(file.toFile())) {
                writer.write(html);
            }
            filesMap.put(indx + " " + url, filePath);
        }
    }
}
