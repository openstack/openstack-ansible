{
    "subject": {
        "commonName": {{ toJson .Subject.CommonName }},
        "organizationalUnit": {{ toJson .OrganizationalUnit }},
        "organization": {{ toJson .Organization }},
        "country": {{ toJson .Country }}
    },
    "sans": {{ toJson .SANs }},
{{- if typeIs "*rsa.PublicKey" .Insecure.CR.PublicKey }}
    "keyUsage": ["keyEncipherment", "digitalSignature"],
{{- else }}
    "keyUsage": ["digitalSignature"],
{{- end }}
    "extKeyUsage": ["serverAuth"]
}
