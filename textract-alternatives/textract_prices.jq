# US East (N. Virginia) synchronous Textract list prices from the AWS Price List API feed.
. as $f | "publicationDate: \($f.publicationDate)",
( [ $f.products[]
    | select(.attributes.regionCode == "us-east-1")
    | select((.attributes.apiType | startswith("Sync")) or .attributes.entityType == "Lending")
    | {name: .attributes.entityType, sku}
    | . + {tiers: [ $f.terms.OnDemand[.sku][].priceDimensions[]
                    | {from: (.beginRange | tonumber), usd: (.pricePerUnit.USD | tonumber)} ]} ]
  | sort_by(.name)[]
  | "\(.name): " + ([.tiers | sort_by(.from)[]
      | "$\(.usd * 100000 | round / 100) per 1,000 pages from page \(.from)"] | join("; ")) )
